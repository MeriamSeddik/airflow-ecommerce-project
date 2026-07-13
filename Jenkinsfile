pipeline {
    agent any
    stages {
        stage('Installation & Test') {
            steps {
                // Installation des dépendances
                sh 'docker exec -u airflow airflow_webserver python -m pip install --user -r requirements.txt'

                // Copie des tests et exécution
                sh 'docker cp tests/. airflow_webserver:/opt/airflow/tests/'
                sh 'docker exec -u airflow airflow_webserver python -m pytest -v /opt/airflow/tests/'
            }
        }

        stage('Validation & Deploy') {
            steps {
                // Validation syntaxique du fichier DAG
                sh 'docker exec -u airflow airflow_webserver python -m py_compile dags/ecommerce_sales_pipeline.py'

                // Déploiement vers Airflow
                sh 'docker cp dags/ecommerce_sales_pipeline.py airflow_webserver:/opt/airflow/dags/'
            }
        }

        stage('Trigger DAG') {
            steps {
                // 1. Attendre que le file system d'Airflow détecte le nouveau fichier
                sh 'sleep 10'

                // 2. Vérifier que le DAG est bien reconnu par Airflow avant de déclencher
                sh 'docker exec -u airflow airflow_webserver airflow dags list | grep ecommerce_sales_pipeline'

                // 3. Déclencher le DAG
                sh 'docker exec -u airflow airflow_webserver airflow dags trigger ecommerce_sales_pipeline'
            }
        }
    }
}