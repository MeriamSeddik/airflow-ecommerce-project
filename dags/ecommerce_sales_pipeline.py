from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime
from pymongo import MongoClient
import pandas as pd
import os
import logging


# --- FONCTIONS DE LOGIQUE ---

def check_file_exists():
    path = '/opt/airflow/data/dataset.csv'
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Le fichier est introuvable à {path}. Assurez-vous qu'il est présent dans le dossier data.")
    logging.info("Fichier détecté avec succès.")


def check_quality_func():
    path = '/opt/airflow/data/dataset.csv'
    if os.path.getsize(path) == 0:
        logging.warning("Le fichier est vide.")
        return 'stop_pipeline'
    return 'process_data'


def process_data_func(**context):
    path = '/opt/airflow/data/dataset.csv'
    df = pd.read_csv(path)

    # Calcul des métriques
    df['total'] = df['Quantity'] * df['UnitPrice']
    valid_mask = (df['Quantity'] > 0) & (df['total'] >= 0)
    df_valid = df[valid_mask].copy()
    df_invalid = df[~valid_mask].copy()

    # Sauvegarde des erreurs
    df_invalid.to_csv('/opt/airflow/data/errors.csv', index=False)

    return {
        "nb_commandes": int(df_valid['InvoiceNo'].nunique()),
        "nb_clients": int(df_valid['CustomerID'].nunique()),
        "chiffre_affaires": float(df_valid['total'].sum()),
        "panier_moyen": float(df_valid.groupby('InvoiceNo')['total'].sum().mean()) if not df_valid.empty else 0,
        "valid_rows": int(len(df_valid)),
        "invalid_rows": int(len(df_invalid))
    }


def store_to_mongo_func(**context):
    ti = context['ti']
    # On récupère les données, si process_data a été skip, metrics sera None
    metrics = ti.xcom_pull(task_ids='process_data')

    if not metrics:
        logging.info("Aucune donnée à traiter, fin du pipeline.")
        return

    # Connexion MongoDB - Utilisation du nom de service 'mongodb'
    try:
        client = MongoClient("mongodb://mongodb:27017/")
        db = client['ecommerce_analytics']
        collection = db['sales_metrics']

        document = {
            "execution_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "dag_id": "ecommerce_sales_pipeline",
            "metrics": metrics
        }
        collection.insert_one(document)
        logging.info("Données insérées dans MongoDB avec succès.")
    except Exception as e:
        logging.error(f"Erreur de connexion MongoDB : {e}")
        raise


# --- DÉFINITION DU DAG ---

default_args = {'owner': 'airflow', 'start_date': datetime(2026, 7, 12)}

with DAG(
        'ecommerce_sales_pipeline',
        default_args=default_args,
        schedule_interval=None,
        catchup=False
) as dag:
    # 1. Vérification simple du fichier
    wait_for_dataset = PythonOperator(
        task_id='wait_for_dataset',
        python_callable=check_file_exists
    )

    # 2. Branchement qualité
    check_quality = BranchPythonOperator(
        task_id='check_quality',
        python_callable=check_quality_func
    )

    # 3. Traitement ou Arrêt
    process_data = PythonOperator(
        task_id='process_data',
        python_callable=process_data_func
    )

    stop_pipeline = EmptyOperator(task_id='stop_pipeline')

    # 4. Rapport final (TriggerRule pour accepter que process_data soit ignoré)
    final_report = PythonOperator(
        task_id='final_report',
        python_callable=store_to_mongo_func,
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS
    )

    # --- DÉPENDANCES ---
    wait_for_dataset >> check_quality
    check_quality >> process_data >> final_report
    check_quality >> stop_pipeline >> final_report