pipeline {
    agent any
    stages {
        stage('Installation & Test') {
            steps {
                // Utilisation de l'utilisateur 'airflow' comme demandé par le conteneur
                sh 'docker exec -u airflow airflow_webserver pip install --user -r requirements.txt'
                sh 'docker exec -u airflow airflow_webserver pytest tests/test_pipeline.py'
            }
        }
        stage('Validation & Deploy') {
            steps {
                sh 'docker exec -u airflow airflow_webserver python -m py_compile dags/*.py'
                // Note : Pour le cp, on reste en root car l'utilisateur airflow n'a peut-être pas le droit d'écrire dans /opt/airflow/dags/
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
