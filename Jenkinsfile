pipeline {
    agent any
    stages {
        stage('Installation & Test') {
            steps {
                // 1. Installation des dépendances
                sh 'docker exec -u airflow airflow_webserver python -m pip install --user -r requirements.txt'
                
                // 2. Copie du dossier tests
                sh 'docker cp tests/. airflow_webserver:/opt/airflow/tests/'
                
                // 3. Debug : Vérification que les fichiers sont bien présents dans le conteneur
                sh 'docker exec -u airflow airflow_webserver ls -la /opt/airflow/tests/'
                
                // 4. Lancement des tests avec mode verbeux sur le dossier
                sh 'docker exec -u airflow airflow_webserver python -m pytest -v /opt/airflow/tests/'
            }
        }
        stage('Validation & Deploy') {
            steps {
                // Validation syntaxique du DAG
                sh 'docker exec -u airflow airflow_webserver python -m py_compile dags/ecommerce_sales_pipeline.py'
                
                // Déploiement vers Airflow
                sh 'docker cp dags/ecommerce_sales_pipeline.py airflow_webserver:/opt/airflow/dags/'
            }
        }
        stage('Trigger DAG') {
            steps {
                sh 'docker exec -u airflow airflow_webserver airflow dags trigger ecommerce_sales_pipeline'
            }
        }
    }
}
