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
                echo 'Installation des dépendances dans airflow_webserver...'
                sh 'docker exec airflow_webserver pip install -r requirements.txt'
            }
        }

        stage('3. Run tests') {
            steps {
                echo 'Exécution des tests unitaires...'
                sh 'docker exec airflow_webserver pytest tests/test_pipeline.py'
            }
        }

        stage('4. Validate DAG') {
            steps {
                echo 'Validation syntaxique du DAG...'
                sh 'docker exec airflow_webserver python -m py_compile dags/*.py'
            }
        }

        stage('5. Deploy DAG') {
            steps {
                echo 'Déploiement du DAG...'
                sh 'docker cp dags/ecommerce_sales_pipeline.py airflow_webserver:/opt/airflow/dags/'
            }
        }

        stage('6. Trigger DAG') {
            steps {
                echo 'Déclenchement du DAG...'
                sh 'docker exec airflow_webserver airflow dags trigger ecommerce_sales_pipeline'
            }
        }

        stage('7. Verify MongoDB') {
            steps {
                echo 'Vérification MongoDB...'
                sh 'docker exec airflow_webserver python scripts/verify_mongo_data.py'
            }
        }
    }

    post {
        success {
            echo 'Pipeline CI/CD terminé avec succès !'
        }
        failure {
            echo 'Le pipeline a échoué. Vérifiez si le conteneur airflow_webserver est bien en ligne.'
        }
    }
}