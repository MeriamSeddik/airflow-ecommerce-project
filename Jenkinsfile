pipeline {
    agent any
    stages {
        stage('Installation & Test') {
            steps {
                sh 'docker exec -u airflow airflow_webserver python -m pip install --user -r requirements.txt'
                sh 'docker cp tests/. airflow_webserver:/opt/airflow/tests/'
                sh 'docker exec -u airflow airflow_webserver python -m pytest -v /opt/airflow/tests/'
            }
        }

        stage('Validation & Deploy') {
            steps {
                sh 'docker exec -u airflow airflow_webserver python -m py_compile dags/ecommerce_sales_pipeline.py'
                // Copie des scripts nécessaires (dossier scripts)
                sh 'docker cp dags/scripts/. airflow_webserver:/opt/airflow/dags/scripts/'
                sh 'docker cp dags/ecommerce_sales_pipeline.py airflow_webserver:/opt/airflow/dags/'
            }
        }

        stage('Trigger DAG') {
            steps {
                sh 'sleep 15'
                // Affiche les erreurs de parsing d'Airflow
                sh 'docker exec -u airflow airflow_webserver airflow dags list-import-errors || true'
                sh 'docker exec -u airflow airflow_webserver airflow dags list | grep ecommerce_sales_pipeline'
                // Déclenchement
                sh 'docker exec -u airflow airflow_webserver airflow dags trigger ecommerce_sales_pipeline'
            }
        }
    }
}