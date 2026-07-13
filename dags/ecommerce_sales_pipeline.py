from datetime import datetime, timedelta
import os
import sys
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor

# Assurer que le dossier dags est bien dans le path pour les imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import corrigé : si ton fichier est dans dags/scripts/check_mongodb.py
from scripts.check_mongodb import run_pipeline

DATA_DIR = '/opt/airflow/data'
TARGET_FILE = 'dataset.csv'

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2026, 7, 12),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'ecommerce_sales_pipeline',
    default_args=default_args,
    description='Pipeline ETL e-commerce',
    schedule_interval=None,
    catchup=False,
    tags=['ecommerce', 'mongodb'],
) as dag:

    wait_for_dataset = FileSensor(
        task_id='wait_for_dataset',
        filepath=TARGET_FILE, # Le FileSensor utilise fs_conn_id, le chemin relatif suffit souvent
        fs_conn_id='fs_default',
        poke_interval=10,
        timeout=60,
        mode='poke',
    )

    process_ecommerce_data = PythonOperator(
        task_id='process_ecommerce_data',
        python_callable=run_pipeline,
    )

    wait_for_dataset >> process_ecommerce_data