from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.sensors.filesystem import FileSensor
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime, timedelta
import pandas as pd
from pymongo import MongoClient
import os


# --- FONCTIONS DE TRAITEMENT ---

def check_quality_func():
    # Points 2, 3 & 4 : Vérification existence, non-vide et qualité minimale
    path = '/opt/airflow/data/dataset.csv'
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return 'stop_pipeline'
    df = pd.read_csv(path)
    if df.empty:
        return 'stop_pipeline'
    return 'process_data'


def process_data_func(**context):
    # Points 6 & 7 : Chargement et calcul des indicateurs
    df = pd.read_csv('/opt/airflow/data/dataset.csv')
    metrics = {
        "total_sales": float(df['sales'].sum()),
        "average_sales": float(df['sales'].mean())
    }
    # Point 8 : Transmission automatique via XComs
    return metrics


def store_to_mongo_func(**context):
    # Point 12 : Stockage dans MongoDB
    ti = context['ti']
    metrics = ti.xcom_pull(task_ids='process_data')

    client = MongoClient("mongodb://root:example@mongodb:27017/")
    db = client['ecommerce_db']
    db.metrics.insert_one({
        "metrics": metrics,
        "timestamp": datetime.now()
    })


# --- DÉFINITION DU DAG ---

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2026, 7, 12),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
        dag_id='ecommerce_sales_pipeline',
        default_args=default_args,
        schedule_interval=None,
        catchup=False
) as dag:
    # Point 1 : FileSensor
    wait_for_dataset = FileSensor(
        task_id='wait_for_dataset',
        filepath='dataset.csv',
        fs_conn_id='fs_default'
    )

    # Point 5 : BranchPythonOperator
    check_quality = BranchPythonOperator(
        task_id='check_quality',
        python_callable=check_quality_func
    )

    stop_pipeline = EmptyOperator(task_id='stop_pipeline')

    process_data = PythonOperator(
        task_id='process_data',
        python_callable=process_data_func
    )

    # Point 9 : Tâches dynamiques
    categories = ['Electronics', 'Clothing', 'Home']
    analysis_tasks = [
        PythonOperator(
            task_id=f'analyze_{cat}',
            python_callable=lambda cat=cat: print(f"Traitement catégorie: {cat}")
        ) for cat in categories
    ]

    # Point 10 & 11 : Rapport final avec Trigger Rules
    final_report = PythonOperator(
        task_id='final_report',
        python_callable=store_to_mongo_func,
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS
    )

    # Flux d'exécution
    wait_for_dataset >> check_quality
    check_quality >> process_data >> analysis_tasks >> final_report
    check_quality >> stop_pipeline >> final_report