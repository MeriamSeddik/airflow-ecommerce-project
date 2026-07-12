pipeline {
    agent any

    stages {
        stage('1. Checkout') {
            steps {
                checkout scm
            }
        }

        stage('2. Install Dependencies') {
            steps {
                // On utilise docker exec pour installer dans le conteneur airflow
                sh 'docker exec airflow-webserver pip install -r requirements.txt'
            }
        }

        stage('3. Run tests') {
            steps {
                // On lance pytest DANS le conteneur airflow
                sh 'docker exec airflow-webserver pytest tests/test_pipeline.py'
            }
        }

        stage('4. Validate DAG') {
            steps {
                // On valide le code à l'intérieur du conteneur airflow
                sh 'docker exec airflow-webserver python -m py_compile dags/*.py'
            }
        }

        stage('5. Deploy DAG') {
            steps {
                // On copie le fichier vers le volume partagé
                sh 'docker cp dags/ecommerce_sales_pipeline.py airflow-webserver:/opt/airflow/dags/'
            }
        }

        stage('6. Trigger DAG') {
            steps {
                sh 'docker exec airflow-webserver airflow dags trigger ecommerce_sales_pipeline'
            }
        }
    }
}