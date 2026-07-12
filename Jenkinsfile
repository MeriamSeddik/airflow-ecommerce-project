pipeline {
    agent any

    environment {
        // Chemin absolu vers le Python de ton environnement virtuel sous Windows
        PYTHON_VENV_EXE = 'C:\\Users\\MERIAM\\PycharmProjects\\airflow-ecommerce-project\\.venv\\Scripts\\python.exe'
        PIP_VENV_EXE    = 'C:\\Users\\MERIAM\\PycharmProjects\\airflow-ecommerce-project\\.venv\\Scripts\\pip.exe'
        PYTEST_VENV_EXE = 'C:\\Users\\MERIAM\\PycharmProjects\\airflow-ecommerce-project\\.venv\\Scripts\\pytest.exe'
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
                echo 'Installation des dépendances dans le venv local...'
                // Utilisation directe du pip de ton projet
                sh "${env.PIP_VENV_EXE} install --upgrade pip"
                sh "${env.PIP_VENV_EXE} install -r requirements.txt"
            }
        }

        stage('3. Run tests') {
            steps {
                echo 'Exécution des tests unitaires avec pytest...'
                sh "${env.PYTEST_VENV_EXE} tests/test_pipeline.py"
            }
        }

        stage('4. Validate DAG') {
            steps {
                echo 'Validation syntaxique du DAG Airflow...'
                sh "${env.PYTHON_VENV_EXE} -m py_compile dags/*.py"
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