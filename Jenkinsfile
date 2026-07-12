pipeline {
    agent any

    stages {
        stage('1. Checkout') {
            steps {
                echo 'Récupération du code source depuis le dépôt Git...'
                checkout scm
            }
        }

        stage('2. Setup & Install') {
            steps {
                echo 'Création de l\'environnement virtuel et installation des dépendances...'
                // On crée un environnement virtuel propre à Jenkins et on installe les paquets
                sh '''
                    python3 -m venv .jenkins-venv
                    . .jenkins-venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('3. Run tests') {
            steps {
                echo 'Exécution des tests unitaires avec pytest...'
                sh '''
                    . .jenkins-venv/bin/activate
                    pytest tests/test_pipeline.py
                '''
            }
        }

        stage('4. Validate DAG') {
            steps {
                echo 'Validation syntaxique du DAG Airflow...'
                sh '''
                    . .jenkins-venv/bin/activate
                    python -m py_compile dags/*.py
                '''
            }
        }

        stage('5. Deploy DAG') {
            steps {
                echo 'Le fichier est disponible pour Airflow via les volumes partagés.'
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