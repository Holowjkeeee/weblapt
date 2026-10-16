pipeline {
    agent any

    environment {
        PYTHON = 'C:\\Program Files\\Python313\\python.exe'
        DEPLOY_DIR = 'C:\\JenkinsDeploy\\weblapt'
    }

    stages {

        stage('Check tools') {
            steps {
                bat '"%PYTHON%" --version'
                bat 'node --version'
                bat 'npm --version'
            }
        }

        stage('Create virtual environment') {
            steps {
                bat 'if exist .venv rmdir /s /q .venv'
                bat '"%PYTHON%" -m venv .venv'
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

        stage('Install frontend dependencies') {
            steps {
                bat 'cd client && npm ci'
            }
        }

        stage('Build frontend') {
            steps {
                bat 'cd client && npm run build'
            }
        }

        stage('Deploy') {
            when {
                branch 'main'
            }

            steps {
                echo 'Deploying application from main branch...'

                bat 'if not exist "%DEPLOY_DIR%" mkdir "%DEPLOY_DIR%"'

                bat '''
                robocopy . "%DEPLOY_DIR%" /E /XD .git .venv node_modules /XF db.sqlite3

                if %ERRORLEVEL% GEQ 8 exit /b %ERRORLEVEL%
                exit /b 0
                '''

                bat '''
                if not exist "%DEPLOY_DIR%\\.venv\\Scripts\\python.exe" (
                    "%PYTHON%" -m venv "%DEPLOY_DIR%\\.venv"
                )
                '''

                bat '"%DEPLOY_DIR%\\.venv\\Scripts\\python.exe" -m pip install -r "%DEPLOY_DIR%\\requirements.txt"'

                bat '"%DEPLOY_DIR%\\.venv\\Scripts\\python.exe" "%DEPLOY_DIR%\\manage.py" migrate'
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully.'
        }

        failure {
            echo 'Pipeline failed. Deployment was not completed.'
        }
    }
}