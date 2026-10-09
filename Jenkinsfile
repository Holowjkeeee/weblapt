pipeline {
    agent any

    stages {
        stage('Check Python') {
            steps {
                bat '"C:\\Program Files\\Python313\\python.exe" --version'
            }
        }

        stage('Create virtual environment') {
            steps {
                bat 'if exist .venv rmdir /s /q .venv'
                bat '"C:\\Program Files\\Python313\\python.exe" -m venv .venv'
            }
        }

        stage('Install Python dependencies') {
            steps {
                bat '.venv\\Scripts\\python.exe -m pip install --upgrade pip'
                bat '.venv\\Scripts\\python.exe -m pip install -r requirements.txt'
            }
        }

        stage('Run Django tests') {
            steps {
                bat '.venv\\Scripts\\python.exe manage.py test'
            }
        }
    }
}