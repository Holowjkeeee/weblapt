
pipeline {
    agent any

    environment {
        PYTHON = 'C:\\Program Files\\Python313\\python.exe'
        DEPLOY_DIR = 'C:\\JenkinsDeploy\\weblapt'
        DOCKER = 'C:\\Users\\Ученик\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe'
        DOCKER_COMPOSE = 'C:\\Users\\Ученик\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker-compose.exe'
    }

    stages {
        stage('Check tools') {
            steps {
                bat '"%PYTHON%" --version'
                bat 'node --version'
                bat 'npm --version'

                echo 'Checking Docker CLI...'
                bat '"%DOCKER%" --version'

                echo 'Checking Docker Compose...'
                bat '"%DOCKER_COMPOSE%" version'

                echo 'Checking Docker Engine connection...'
                bat '"%DOCKER%" info --format "{{.ServerVersion}}"'
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

        /*
         * Временная проверка запуска приложения.
         *
         * Backend test  = 8100
         * Frontend test = 4174
         */
        stage('Check application startup') {
            steps {
                echo 'Starting temporary Django backend...'

                bat '''
                start "" /B cmd /C ".venv\\Scripts\\python.exe manage.py runserver 127.0.0.1:8100 --noreload > backend-test.log 2>&1"
                '''

                bat '''
                powershell -NoProfile -Command "$limit=(Get-Date).AddSeconds(60); while((Get-Date) -lt $limit) { try { $r=Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:8100/api/auth/csrf/' -TimeoutSec 3; if ($r.StatusCode -eq 200) { Write-Host 'Backend startup check SUCCESS'; exit 0 } } catch {}; Start-Sleep -Seconds 2 }; Write-Host 'Backend startup check FAILED'; exit 1"
                '''

                echo 'Starting temporary Vue frontend...'

                bat '''
                start "" /B cmd /C "cd client && npm run preview -- --host 127.0.0.1 --port 4174 > ..\\frontend-test.log 2>&1"
                '''

                bat '''
                powershell -NoProfile -Command "$limit=(Get-Date).AddSeconds(60); while((Get-Date) -lt $limit) { try { $r=Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:4174/' -TimeoutSec 3; if ($r.StatusCode -eq 200) { Write-Host 'Frontend startup check SUCCESS'; exit 0 } } catch {}; Start-Sleep -Seconds 2 }; Write-Host 'Frontend startup check FAILED'; exit 1"
                '''

                echo 'Backend and frontend startup checks passed.'
            }

            post {
                failure {
                    bat '''
                    echo ============================
                    echo BACKEND LOG
                    echo ============================

                    if exist backend-test.log type backend-test.log

                    echo.
                    echo ============================
                    echo FRONTEND LOG
                    echo ============================

                    if exist frontend-test.log type frontend-test.log
                    '''
                }

                always {
                    echo 'Stopping temporary test servers...'

                    bat '''
                    powershell -NoProfile -Command "$p=Get-NetTCPConnection -LocalPort 8100 -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique; if($p){Stop-Process -Id $p -Force -ErrorAction SilentlyContinue}"

                    powershell -NoProfile -Command "$p=Get-NetTCPConnection -LocalPort 4174 -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique; if($p){Stop-Process -Id $p -Force -ErrorAction SilentlyContinue}"

                    exit /b 0
                    '''
                }
            }
        }

        /*
         * Docker CI: сборка образа Django.
         */
        stage('Build Docker backend image') {
            steps {
                echo 'Building Django Docker image...'

                bat '"%DOCKER%" build -t weblapt-backend:ci -f Dockerfile .'
            }
        }

        /*
         * Docker CI: сборка образа Nginx с Vue.
         */
        stage('Build Docker nginx image') {
            steps {
                echo 'Building Nginx Docker image with Vue frontend...'

                bat '"%DOCKER%" build -t weblapt-nginx:ci -f nginx\\Dockerfile .'
            }
        }

        stage('Test Docker Compose deployment') {
    steps {
        withEnv([
            'APP_PORT=8082',
            'BACKEND_IMAGE=weblapt-backend:ci',
            'NGINX_IMAGE=weblapt-nginx:ci'
        ]) {
            echo 'Validating Docker Compose configuration...'
            bat '"%DOCKER_COMPOSE%" -p weblapt-ci config --quiet'

            echo 'Starting temporary Docker containers...'
            bat '"%DOCKER_COMPOSE%" -p weblapt-ci up -d --no-build --wait --wait-timeout 90'

            echo 'Checking container status...'
            bat '"%DOCKER_COMPOSE%" -p weblapt-ci ps'

            echo 'Checking Vue frontend through Nginx...'
            bat 'curl.exe --fail --silent --show-error http://127.0.0.1:8082/ > NUL'

            echo 'Checking Django API through Nginx...'
            bat 'curl.exe --fail --silent --show-error http://127.0.0.1:8082/api/auth/csrf/ > NUL'

            echo 'Docker integration tests passed.'
        }
    }

    post {
        failure {
            withEnv([
                'APP_PORT=8082',
                'BACKEND_IMAGE=weblapt-backend:ci',
                'NGINX_IMAGE=weblapt-nginx:ci'
            ]) {
                bat(returnStatus: true, script: '"%DOCKER_COMPOSE%" -p weblapt-ci logs --tail 80')
            }
        }

        always {
            withEnv([
                'APP_PORT=8082',
                'BACKEND_IMAGE=weblapt-backend:ci',
                'NGINX_IMAGE=weblapt-nginx:ci'
            ]) {
                echo 'Cleaning up test containers...'
                bat '"%DOCKER_COMPOSE%" -p weblapt-ci down -v --remove-orphans'
            }
        }
    }
}
       
stage('Deploy Docker application') {
    when {
        branch 'main'
    }

    steps {
        echo 'Preparing Docker images for production...'

        bat '"%DOCKER%" tag weblapt-backend:ci weblapt-backend:latest'
        bat '"%DOCKER%" tag weblapt-nginx:ci weblapt-nginx:latest'

        withEnv([
            'APP_PORT=8081',
            'BACKEND_IMAGE=weblapt-backend:latest',
            'NGINX_IMAGE=weblapt-nginx:latest'
        ]) {
            echo 'Validating production configuration...'
            bat '"%DOCKER_COMPOSE%" -p weblapt config --quiet'

            echo 'Deploying Docker containers...'
            bat '"%DOCKER_COMPOSE%" -p weblapt up -d --no-build --force-recreate --wait --wait-timeout 90'

            echo 'Checking production containers...'
            bat '"%DOCKER_COMPOSE%" -p weblapt ps'

            echo 'Checking production frontend...'
            bat 'curl.exe --fail --silent --show-error http://127.0.0.1:8081/ > NUL'

            echo 'Checking production Django API...'
            bat 'curl.exe --fail --silent --show-error http://127.0.0.1:8081/api/auth/csrf/ > NUL'
        }

        echo 'Production deployment completed successfully.'
        echo 'Application URL: http://localhost:8081'
    }
}


    post {
        success {
            echo 'Pipeline completed successfully.'
        }

        failure {
            echo 'Pipeline failed. Deployment was not completed successfully.'
        }
    }
}
