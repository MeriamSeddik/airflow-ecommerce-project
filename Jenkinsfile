pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Installation & Test') {
            steps {
                // On utilise le chemin complet vers l'exécutable Docker
                sh '/usr/bin/docker exec airflow_webserver pip install -r requirements.txt'
                sh '/usr/bin/docker exec airflow_webserver pytest tests/test_pipeline.py'
            }
        }
        stage('Validation & Deploy') {
            steps {
                sh '/usr/bin/docker exec airflow_webserver python -m py_compile dags/*.py'
                sh '/usr/bin/docker cp dags/ecommerce_sales_pipeline.py airflow_webserver:/opt/airflow/dags/'
            }
        }
        stage('Trigger DAG') {
            steps {
                sh '/usr/bin/docker exec airflow_webserver airflow dags trigger ecommerce_sales_pipeline'
            }
        }
    }
}