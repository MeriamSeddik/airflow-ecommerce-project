pipeline {
    agent any
    stages {
        stage('Checkout') { steps { checkout scm } }
        stage('Install dependencies') { steps { sh 'docker exec -u airflow airflow_webserver pip install -r requirements.txt' } }
        stage('Run tests') { steps { sh 'docker exec -u airflow airflow_webserver pytest tests/' } }
        stage('Validate DAG') { steps { sh 'docker exec -u airflow airflow_webserver python -m py_compile dags/ecommerce_sales_pipeline.py' } }
        stage('Deploy DAG') {
            steps {
                sh 'docker cp dags/ecommerce_sales_pipeline.py airflow_webserver:/opt/airflow/dags/'
                sh 'docker cp scripts/. airflow_webserver:/opt/airflow/dags/scripts/'
            }
        }
        stage('Trigger DAG') {
            steps {
                sh 'docker exec -u airflow airflow_webserver airflow dags unpause ecommerce_sales_pipeline || true'
                sh 'docker exec -u airflow airflow_webserver airflow dags trigger ecommerce_sales_pipeline'
            }
        }
        stage('Verify MongoDB') {
            steps {
                // On attend quelques secondes que le job tourne
                sh 'sleep 30'
                sh 'docker exec -u airflow airflow_webserver python /opt/airflow/tests/verify_mongo.py'
            }
        }
    }
}