from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.sensors.filesystem import FileSensor
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime, timedelta
import pandas as pd
from pymongo import MongoClient
import os


# --- FONCTIONS ---

def check_quality_func():
    path = '/opt/airflow/data/dataset.csv'
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return 'stop_pipeline'
    return 'process_data'


def process_data_func(**context):
    path = '/opt/airflow/data/dataset.csv'
    df = pd.read_csv(path)

    # Règle : Montant (UnitPrice * Quantity) >= 0 et Quantity > 0
    df['total'] = df['Quantity'] * df['UnitPrice']

    # Identification des lignes valides vs invalides
    valid_mask = (df['Quantity'] > 0) & (df['total'] >= 0)

    df_valid = df[valid_mask].copy()
    df_invalid = df[~valid_mask].copy()

    # Sauvegarde des erreurs
    df_invalid.to_csv('/opt/airflow/data/errors.csv', index=False)

    # Calcul des métriques
    metrics = {
        "nb_commandes": int(df_valid['InvoiceNo'].nunique()),
        "nb_clients": int(df_valid['CustomerID'].nunique()),
        "chiffre_affaires": float(df_valid['total'].sum()),
        "panier_moyen": float(df_valid.groupby('InvoiceNo')['total'].sum().mean()) if not df_valid.empty else 0,
        "valid_rows": int(len(df_valid)),
        "invalid_rows": int(len(df_invalid))
    }
    return metrics


def store_to_mongo_func(**context):
    ti = context['ti']
    metrics = ti.xcom_pull(task_ids='process_data')

    client = MongoClient("mongodb://mongodb:27017/")
    db = client['ecommerce_analytics']
    collection = db['sales_metrics']

    document = {
        "execution_date": datetime.now().strftime("%Y-%m-%d"),
        "dag_id": "ecommerce_sales_pipeline",
        "dataset": "olist",
        "source_file": "dataset.csv",
        "status": "success" if metrics else "failed",
        "global_metrics": {
            "nb_commandes": metrics.get("nb_commandes"),
            "nb_clients": metrics.get("nb_clients"),
            "chiffre_affaires": metrics.get("chiffre_affaires"),
            "panier_moyen": metrics.get("panier_moyen")
        },
        "quality": {
            "valid_rows": metrics.get("valid_rows"),
            "invalid_rows": metrics.get("invalid_rows"),
            "error_file": "errors.csv"
        }
    }
    collection.insert_one(document)


# --- DAG ---

default_args = {'owner': 'airflow', 'start_date': datetime(2026, 7, 12)}

with DAG('ecommerce_sales_pipeline', default_args=default_args, schedule_interval=None, catchup=False) as dag:
    wait_for_dataset = FileSensor(task_id='wait_for_dataset', filepath='dataset.csv', fs_conn_id='fs_default')
    check_quality = BranchPythonOperator(task_id='check_quality', python_callable=check_quality_func)
    stop_pipeline = EmptyOperator(task_id='stop_pipeline')
    process_data = PythonOperator(task_id='process_data', python_callable=process_data_func)
    final_report = PythonOperator(
        task_id='final_report',
        python_callable=store_to_mongo_func,
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS
    )

    wait_for_dataset >> check_quality >> [process_data, stop_pipeline]
    [process_data, stop_pipeline] >> final_report