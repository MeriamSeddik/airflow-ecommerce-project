pipeline {
    agent any
    stages {
        stage('Installation & Test') {
            steps {
                sh 'docker exec -u airflow airflow_webserver python -m pip install --user -r requirements.txt'
                
                // On copie tout le contenu du dossier tests vers le conteneur
                sh 'docker cp tests/. airflow_webserver:/opt/airflow/tests/'
                
                // On lance pytest en ciblant explicitement le fichier
                sh 'docker exec -u airflow airflow_webserver python -m pytest /opt/airflow/tests/test_pipeline.py'
            }
        }
        stage('Validation & Deploy') {
            steps {
                // Attention : tes dags sont dans dags/ecommerce_sales_pipeline.py
                sh 'docker exec -u airflow airflow_webserver python -m py_compile dags/ecommerce_sales_pipeline.py'
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
