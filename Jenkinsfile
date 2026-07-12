pipeline {
    // On dit à Jenkins d'exécuter le pipeline dans un conteneur Python temporaire
    agent {
        docker {
            image 'python:3.10-slim'
        }
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
                echo 'Installation des dépendances dans l\'environnement isolé...'
                sh '''
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
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
                echo 'Le code a été validé avec succès et est prêt à tourner sur Airflow !'
            }
        }
    }

    post {
        success {
            echo 'Super ! Le pipeline Jenkins est entièrement au VERT !'
        }
        failure {
            echo 'Erreur détectée dans le pipeline Jenkins.'
        }
    }
}