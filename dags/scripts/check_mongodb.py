import pandas as pd
from pymongo import MongoClient
from datetime import datetime
import os


def run_pipeline():
    # 1. Chemins des fichiers (Configurés pour tes volumes Docker)
    input_file = '/opt/airflow/data/dataset.csv'
    error_file = '/opt/airflow/data/error_dataset.csv'

    print(f"Lecture du fichier : {input_file}")

    # Sécurité : Vérifier si le fichier existe et n'est pas vide
    if not os.path.exists(input_file) or os.path.getsize(input_file) == 0:
        print("Erreur : Le fichier est vide ou inexistant.")
        return "stop_pipeline"  # Utile pour le BranchPythonOperator

    df = pd.read_csv(input_file)
    total_rows = len(df)

    # 2. Règles de gestion & Contrôle qualité
    # Une ligne est invalide si : Quantité <= 0 ou Prix <= 0 ou Montant négatif
    # (On recalcule le Montant au passage si absent : Quantité * Prix)
    if 'UnitPrice' in df.columns and 'Quantity' in df.columns:
        df['Montant'] = df['Quantity'] * df['UnitPrice']
    elif 'Price' in df.columns and 'Quantity' in df.columns:
        df['Montant'] = df['Quantity'] * df['Price']
    else:
        df['Montant'] = 0

    # Séparation lignes valides / invalides
    condition_valide = (df['Quantity'] > 0) & (df['Montant'] > 0)
    df_valid = df[condition_valide].copy()
    df_invalid = df[~condition_valide].copy()

    # Sauvegarde des erreurs
    if not df_invalid.empty:
        df_invalid.to_csv(error_file, index=False)
        print(f"{len(df_invalid)} lignes incorrectes isolées dans {error_file}")

    valid_count = len(df_valid)
    invalid_count = len(df_invalid)

    if valid_count == 0:
        print("Aucune donnée valide à traiter.")
        return "partial"

    # 3. Calcul des indicateurs métier (KPIs)
    # Note : Adapte les noms de colonnes ('InvoiceNo', 'CustomerID', 'Description', 'Country')
    # selon ton dataset exact s'ils changent.

    nb_commandes = int(df_valid['InvoiceNo'].nunique()) if 'InvoiceNo' in df_valid.columns else 0
    nb_clients = int(df_valid['CustomerID'].nunique()) if 'CustomerID' in df_valid.columns else 0
    chiffre_affaires = float(df_valid['Montant'].sum())
    panier_moyen = float(chiffre_affaires / nb_commandes) if nb_commandes > 0 else 0.0

    # Top 10 des produits les plus vendus (par quantité)
    prod_col = 'Description' if 'Description' in df_valid.columns else 'Produit'
    top_products_df = df_valid.groupby(prod_col).agg(
        sales=('Quantity', 'sum'),
        revenue=('Montant', 'sum')
    ).sort_values(by='sales', ascending=False).head(10).reset_index()

    top_products = []
    for _, row in top_products_df.iterrows():
        top_products.append({
            "product": str(row[prod_col]),
            "sales": int(row['sales']),
            "revenue": float(row['revenue'])
        })

    # Chiffre d'affaires par Région / Pays
    region_col = 'Country' if 'Country' in df_valid.columns else 'Région'
    region_df = df_valid.groupby(region_col).agg(
        orders=('InvoiceNo', 'nunique'),
        revenue=('Montant', 'sum')
    ).reset_index()

    region_metrics = []
    for _, row in region_df.iterrows():
        region_metrics.append({
            "region": str(row[region_col]),
            "orders": int(row['orders']),
            "revenue": float(row['revenue'])
        })

    # 4. Construction du JSON final pour MongoDB
    mongo_document = {
        "execution_date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "dag_id": "ecommerce_sales_pipeline",
        "dataset": "online_retail",  # ou olist selon ton choix
        "source_file": "dataset.csv",
        "status": "success" if invalid_count == 0 else "partial",
        "global_metrics": {
            "nb_commandes": nb_commandes,
            "nb_clients": nb_clients,
            "chiffre_affaires": round(chiffre_affaires, 2),
            "panier_moyen": round(panier_moyen, 2)
        },
        "top_products": top_products,
        "region_metrics": region_metrics,
        "quality": {
            "valid_rows": valid_count,
            "invalid_rows": invalid_count,
            "error_file": "error_dataset.csv"
        }
    }

    # 5. Stockage dans MongoDB
    try:
        # Connexion au conteneur Mongo via le réseau Docker (nom du service : mongodb)
        client = MongoClient('mongodb://mongodb:27017/', serverSelectionTimeoutMS=5000)
        db = client['ecommerce_analytics']
        collection = db['sales_metrics']

        # Insertion du document
        collection.insert_one(mongo_document)
        print("Indicateurs insérés avec succès dans MongoDB (ecommerce_analytics.sales_metrics) !")
    except Exception as e:
        print(f"Erreur lors de l'insertion MongoDB : {e}")
        raise


if __name__ == "__main__":
    run_pipeline()