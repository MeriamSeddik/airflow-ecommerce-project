pipeline {
    agent any

    stages {
        stage('1. Checkout') {
            steps {
                echo 'Récupération du code source depuis le dépôt Git...'
                checkout scm
            }
        }

        stage('2. Install Python & Dependencies') {
            steps {
                echo 'Installation de Python et des dépendances dans le conteneur Jenkins...'
                // On installe Python, on crée un venv Linux et on installe les packages
                sh '''
                    current_user=$(whoami)
                    if [ "$current_user" = "root" ]; then
                        apt-get update && apt-get install -y python3 python3-pip python3-venv
                    else
                        sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv
                    fi

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
                    python3 -m py_compile dags/*.py
                '''
            }
        }

        stage('5. Deploy DAG') {
            steps {
                echo 'Le code a été validé avec succès !'
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