pipeline {
    agent any
    stages {
        stage('Installation & Test') {
            steps {
                // 1. Installation des dépendances
                sh 'docker exec -u airflow airflow_webserver python -m pip install --user -r requirements.txt'
                
                // 2. CORRECTION : Copie du dossier tests dans le conteneur
                // On utilise root pour copier car le dossier /opt/airflow appartient à root
                sh 'docker cp tests/ airflow_webserver:/opt/airflow/'
                
                // 3. Lancement des tests
                sh 'docker exec -u airflow airflow_webserver python -m pytest tests/test_pipeline.py'
            }
        }
        stage('Validation & Deploy') {
            steps {
                sh 'docker exec -u airflow airflow_webserver python -m py_compile dags/*.py'
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
