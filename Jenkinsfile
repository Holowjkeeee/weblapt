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

        stage('Check application startup') {
            steps {
                echo 'Starting Django backend...'

                bat '''
                start "" /B .venv\\Scripts\\python.exe manage.py runserver 127.0.0.1:8000 --noreload > backend-test.log 2>&1

                echo Waiting for Django backend...

                curl.exe --fail --silent --show-error --output NUL --retry 20 --retry-delay 1 --retry-connrefused http://127.0.0.1:8000/api/auth/csrf/

                if errorlevel 1 exit /b 1

                echo Django backend started successfully.
                '''

                echo 'Starting Vue production build...'

                bat '''
                cd client

                start "" /B cmd /C "npm run preview -- --host 127.0.0.1 --port 4173 > ..\\frontend-test.log 2>&1"

                cd ..

                echo Waiting for Vue frontend...

                curl.exe --fail --silent --show-error --output NUL --retry 20 --retry-delay 1 --retry-connrefused http://127.0.0.1:4173/

                if errorlevel 1 exit /b 1

                echo Vue frontend started successfully.
                '''

                echo 'Backend and frontend startup checks passed.'
            }

            post {
                failure {
                    bat '''
                    echo ==============================
                    echo BACKEND TEST LOG
                    echo ==============================

                    if exist backend-test.log type backend-test.log

                    echo.
                    echo ==============================
                    echo FRONTEND TEST LOG
                    echo ==============================

                    if exist frontend-test.log type frontend-test.log
                    '''
                }

                always {
                    echo 'Stopping temporary test servers...'

                    bat '''
                    powershell -NoProfile -Command "$p = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique; if ($p) { Stop-Process -Id $p -Force -ErrorAction SilentlyContinue }"

                    powershell -NoProfile -Command "$p = Get-NetTCPConnection -LocalPort 4173 -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique; if ($p) { Stop-Process -Id $p -Force -ErrorAction SilentlyContinue }"

                    exit /b 0
                    '''
                }
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
                robocopy . "%DEPLOY_DIR%" /E /XD .git .venv node_modules /XF db.sqlite3 backend-test.log frontend-test.log

                if %ERRORLEVEL% GEQ 8 exit /b %ERRORLEVEL%
                exit /b 0
                '''

                bat '''
                if not exist "%DEPLOY_DIR%\\.venv\\Scripts\\python.exe" (
                    "%PYTHON%" -m venv "%DEPLOY_DIR%\\.venv"
                )
                '''

                bat '"%DEPLOY_DIR%\\.venv\\Scripts\\python.exe" -m pip install -r "%DEPLOY_DIR%\\requirements.txt"'

                bat '"%DEPLOY_DIR%\\.venv\\Scripts\\python.exe" "%DEPLOY_DIR%\\manage.py" check'

                bat '"%DEPLOY_DIR%\\.venv\\Scripts\\python.exe" "%DEPLOY_DIR%\\manage.py" migrate'

                bat 'if not exist "%DEPLOY_DIR%\\client\\dist\\index.html" exit /b 1'

                echo 'Deployment completed successfully.'
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully.'
        }

        failure {
            echo 'Pipeline failed. Deployment was not performed.'
        }
    }
}