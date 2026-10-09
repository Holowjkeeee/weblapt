pipeline {
    agent any

    stages {
        stage('Install Python dependencies') {
            steps {
                bat 'python -m pip install -r requirements.txt'
            }
        }

        stage('Run Django tests') {
            steps {
                bat 'python manage.py test'
            }
        }
    }
}