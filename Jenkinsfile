pipeline {
    agent any

    environment {
        // Remplace par le nom exact de ton conteneur Airflow qui possède la CLI (souvent airflow-scheduler ou airflow-webserver)
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
                echo 'Installation des dépendances Python...'
                sh 'pip install --upgrade pip'
                sh 'pip install -r requirements.txt'
            }
        }

        stage('3. Run tests') {
            steps {
                echo 'Exécution des tests unitaires avec pytest...'
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
                sh 'python scripts/check_mongodb.py'
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