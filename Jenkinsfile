pipeline {
    agent any

    stages {
        stage('1. Checkout') {
            steps {
                echo 'Récupération du code source depuis Git...'
                checkout scm
            }
        }

        stage('2. Install Dependencies') {
            steps {
                echo 'Installation des dépendances Python...'
                sh 'pip install -r requirements.txt'
            }
        }

        stage('3. Run tests') {
            steps {
                echo 'Exécution des tests avec pytest...'
                sh 'pytest tests/test_pipeline.py'
            }
        }

        stage('4. Validate DAG') {
            steps {
                echo 'Validation syntaxique du DAG Airflow...'
                sh 'python -m py_compile dags/*.py'
            }
        }

        stage('5. Deploy DAG') {
            steps {
                echo 'Déploiement du DAG...'
                sh 'cp dags/ecommerce_sales_pipeline.py docker/dags/'
            }
        }

        stage('6. Trigger DAG') {
            steps {
                echo 'Déclenchement du DAG Airflow...'
                sh 'docker exec airflow-webserver airflow dags trigger ecommerce_sales_pipeline'
            }
        }

        stage('7. Verify MongoDB') {
            steps {
                echo 'Vérification des données dans MongoDB...'
                // Script de vérification simple pour valider la présence de données
                sh 'python scripts/verify_mongo_data.py'
            }
        }
    }

    post {
        success {
            echo 'Pipeline CI/CD complet terminé avec succès !'
        }
        failure {
            echo 'Le pipeline a échoué. Vérifiez les logs des étapes.'
        }
    }
}