import sys
import os

# Ajout du répertoire courant aux chemins système pour permettre l'import des scripts
sys.path.append('/opt/airflow/dags')

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor

# Import robuste avec gestion d'erreur
try:
    from scripts.check_mongodb import run_pipeline
except ImportError as e:
    print(f"CRITICAL IMPORT ERROR: {e}")
    def run_pipeline():
        raise ImportError(f"Impossible de charger le script: {e}")

DATA_DIR = '/opt/airflow/data'
TARGET_FILE = 'dataset.csv'

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2026, 7, 12),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='ecommerce_sales_pipeline',
    default_args=default_args,
    description='Pipeline ETL e-commerce',
    schedule_interval=None,
    catchup=False,
    tags=['ecommerce', 'mongodb'],
) as dag:


    wait_for_dataset = FileSensor(
        task_id='wait_for_dataset',
        filepath='data/dataset.csv',
        fs_conn_id='fs_default',
        poke_interval=10,
        timeout=120,
        mode='poke',
    )

    process_ecommerce_data = PythonOperator(
        task_id='process_ecommerce_data',
        python_callable=run_pipeline,
    )

    wait_for_dataset >> process_ecommerce_data