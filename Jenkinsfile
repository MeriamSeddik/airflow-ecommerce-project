pipeline {
    agent any
    stages {
        stage('Installation & Test') {
            steps {
                // Utilisation de python -m pip pour garantir le bon chemin d'accès
                sh 'docker exec -u airflow airflow_webserver python -m pip install --user -r requirements.txt'
                
                // Idem pour pytest
                sh 'docker exec -u airflow airflow_webserver python -m pytest tests/test_pipeline.py'
            }
        }
        stage('Validation & Deploy') {
            steps {
                sh 'docker exec -u airflow airflow_webserver python -m py_compile dags/*.py'
                // La copie doit rester en root pour avoir les droits d'écriture dans /opt/airflow/dags/
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
