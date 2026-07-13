pipeline {
    agent any
    stages {
        stage('Installation & Test') {
            steps {
                // On utilise -u 0 (identifiant numérique de root) pour garantir les droits
                sh 'docker exec -u 0 airflow_webserver pip install -r requirements.txt'
                sh 'docker exec -u 0 airflow_webserver pytest tests/test_pipeline.py'
            }
        }
        stage('Validation & Deploy') {
            steps {
                sh 'docker exec -u 0 airflow_webserver python -m py_compile dags/*.py'
                sh 'docker cp dags/ecommerce_sales_pipeline.py airflow_webserver:/opt/airflow/dags/'
            }
        }
        stage('Trigger DAG') {
            steps {
                sh 'docker exec airflow_webserver airflow dags trigger ecommerce_sales_pipeline'
            }
        }
    }
}
