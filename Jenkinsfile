pipeline {
    agent any

    stages {
        stage('Install Python dependencies') {
            steps {
                bat '"C:\\Users\\Ученик\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe" -m pip install -r requirements.txt'
            }
        }

        stage('Run Django tests') {
            steps {
                bat '"C:\\Users\\Ученик\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe" manage.py test'
            }
        }
    }
}