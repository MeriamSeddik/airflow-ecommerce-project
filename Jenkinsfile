pipeline {
    agent any
    stages {
        stage('Installation & Test') {
            steps {
                // Installation des dépendances dans le conteneur
                sh 'docker exec -u airflow airflow_webserver python -m pip install --user -r requirements.txt'

                // Copie des tests et exécution avec pytest
                sh 'docker cp tests/. airflow_webserver:/opt/airflow/tests/'
                sh 'docker exec -u airflow airflow_webserver python -m pytest -v /opt/airflow/tests/'
            }
        }

        stage('Validation & Deploy') {
            steps {
                // Validation de la syntaxe du fichier DAG
                sh 'docker exec -u airflow airflow_webserver python -m py_compile dags/ecommerce_sales_pipeline.py'

                // Déploiement des scripts et du DAG
                sh 'docker cp dags/scripts/. airflow_webserver:/opt/airflow/dags/scripts/'
                sh 'docker cp dags/ecommerce_sales_pipeline.py airflow_webserver:/opt/airflow/dags/'
            }
        }

        stage('Trigger DAG') {
            steps {
                // Attente pour que le scheduler Airflow détecte les nouveaux fichiers
                sh 'sleep 15'

                // 1. Activer le DAG (le sortir du mode 'paused' par défaut)
                sh 'docker exec -u airflow airflow_webserver airflow dags unpause ecommerce_sales_pipeline || true'

                // 2. Forcer la resérialisation de la base de données
                sh 'docker exec -u airflow airflow_webserver airflow dags reserialize'

                // 3. Afficher les erreurs de parsing s'il y en a
                sh 'docker exec -u airflow airflow_webserver airflow dags list-import-errors || true'

                // 4. Déclencher le DAG
                sh 'docker exec -u airflow airflow_webserver airflow dags trigger ecommerce_sales_pipeline'
            }
        }
    }
}