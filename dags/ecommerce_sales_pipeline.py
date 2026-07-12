from datetime import datetime, timedelta
import os
import sys
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor

# Fixer le problème d'import en ajoutant le dossier racine d'Airflow au path Python
AIRFLOW_HOME = os.getenv('AIRFLOW_HOME', '/opt/airflow')
if AIRFLOW_HOME not in sys.path:
    sys.path.append(AIRFLOW_HOME)

# Import de la fonction de nettoyage depuis ton script scripts/check_mongodb.py
from dags.scripts.check_mongodb import run_pipeline
# Chemins des fichiers à l'intérieur du conteneur Airflow
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
    description='Pipeline ETL e-commerce avec détection d\'anomalies et stockage MongoDB',
    schedule_interval=None,  # Déclenchement manuel ou via Jenkins/API
    catchup=False,
    tags=['ecommerce', 'mongodb'],
) as dag:

    # 1. Capteur (Sensor) : Vérifie si le fichier dataset.csv est présent dans le dossier data
    wait_for_dataset = FileSensor(
        task_id='wait_for_dataset',
        filepath=os.path.join(DATA_DIR, TARGET_FILE),  # Chemin absolu complet sécurisé
        fs_conn_id='fs_default',  # Connexion de système de fichiers par défaut d'Airflow
        poke_interval=10,         # Vérifie toutes les 10 secondes
        timeout=60,               # S'arrête après 1 minute si pas de fichier
        mode='poke',
    )

    # 2. Opérateur Python : Lance notre script de traitement validé à l'étape précédente
    process_ecommerce_data = PythonOperator(
        task_id='process_ecommerce_data',
        python_callable=run_pipeline,
    )

    # Définition de l'ordre d'exécution : d'abord le capteur, puis le script
    wait_for_dataset >> process_ecommerce_data