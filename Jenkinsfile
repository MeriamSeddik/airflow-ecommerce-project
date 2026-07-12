pipeline {
    agent any

    environment {
        // Nom de ton conteneur Airflow (ex: airflow-scheduler ou le nom généré par docker-compose)
        AIRFLOW_CONTAINER = 'airflow-scheduler'
    }

    stages {
        stage('1. Checkout') {
            steps {
                echo 'Récupération du code source depuis le dépôt Git...'
                checkout scm
            }
        }

        stage('2. Install dependencies') {
            steps {
                echo 'Installation des dépendances Python dans le conteneur Airflow...'
                // On exécute la commande direct dans le conteneur Airflow
                sh "docker exec -t ${env.AIRFLOW_CONTAINER} pip install --upgrade pip"
                sh "docker exec -t ${env.AIRFLOW_CONTAINER} pip install -r requirements.txt"
            }
        }

        stage('3. Run tests') {
            steps {
                echo 'Exécution des tests unitaires avec pytest dans Airflow...'
                sh "docker exec -t ${env.AIRFLOW_CONTAINER} pytest tests/test_pipeline.py"
            }
        }

        stage('4. Validate DAG') {
            steps {
                echo 'Validation syntaxique du DAG Airflow...'
                sh "docker exec -t ${env.AIRFLOW_CONTAINER} python -m py_compile dags/ecommerce_sales_pipeline.py"
            }
        }

        stage('5. Deploy DAG') {
            steps {
                echo 'Déploiement du DAG vers le dossier synchronisé d\'Airflow...'
                echo 'Le fichier est copié/partagé automatiquement via les volumes Docker.'
            }
        }

        stage('6. Trigger DAG') {
            steps {
                echo 'Déclenchement du DAG Airflow via la ligne de commande...'
                sh "docker exec -t ${env.AIRFLOW_CONTAINER} airflow dags trigger ecommerce_sales_pipeline"
            }
        }

        stage('7. Verify MongoDB') {
            steps {
                echo 'Vérification finale des indicateurs stockés dans MongoDB...'
                sh "docker exec -t ${env.AIRFLOW_CONTAINER} python scripts/check_mongodb.py"
            }
        }
    }

    post {
        success {
            echo 'Super ! Le pipeline Jenkins est entièrement au VERT !'
        }
        failure {
            echo 'Erreur détectée dans le pipeline Jenkins. Regarde les logs de l\'étape concernée.'
        }
    }
}