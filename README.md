# Airflow E-commerce Pipeline

Projet de pipeline ETL automatisé pour l'analyse de données e-commerce.

## 🚀 Présentation
Ce projet automatise le traitement de fichiers de ventes :
- **Ingestion & Nettoyage** : Isolation des données invalides.
- **Transformation** : Calcul de KPIs (Chiffre d'affaires, panier moyen, top produits).
- **Stockage** : Persistance des résultats dans MongoDB.
- **CI/CD** : Intégration continue via Jenkins.

## 🛠 Stack Technique
- **Orchestrateur** : Apache Airflow
- **Base de données** : MongoDB
- **Langage** : Python (Pandas)
- **Environnement** : Docker / Docker Compose

## ⚙️ Utilisation
1. Lancer les services :
   ```bash
   docker compose up -d
 2. Accéder à l'interface Airflow : `http://localhost:8080`
3. Vérifier les données dans MongoDB :
   - Base : `ecommerce_analytics`
   - Collection : `sales_metrics`

## 📁 Structure du dépôt
- `dags/` : Script du pipeline Airflow.
- `scripts/` : Logique de traitement des données.
- `Jenkinsfile` : Configuration du pipeline CI/CD.
- `data/` : Dossier pour les fichiers sources et les rapports d'erreurs.

## 📊 Résultat attendu
Après l'exécution du DAG, les métriques sont calculées et stockées au format JSON dans MongoDB, permettant un suivi historique des performances commerciales.  