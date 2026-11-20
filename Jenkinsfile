
pipeline {
    agent any

    options {
        disableConcurrentBuilds()
    }

    environment {
        PYTHON = 'C:\\Program Files\\Python313\\python.exe'
        DOCKER = 'C:\\Users\\Ученик\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe'
        DOCKER_COMPOSE = 'C:\\Users\\Ученик\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker-compose.exe'
    }

    stages {
        stage('Prepare build') {
            steps {
                script {
                    def branch = (env.BRANCH_NAME ?: 'manual').toLowerCase().replaceAll(/[^a-z0-9_.-]/, '-')
                    env.IMAGE_TAG = "${branch}-${env.BUILD_NUMBER}"
                    echo "Docker image tag: ${env.IMAGE_TAG}"
                }
            }
        }

        stage('Check tools') {
            steps {
                bat '"%PYTHON%" --version'
                bat 'node --version'
                bat 'npm --version'
                bat '"%DOCKER%" --version'
                bat '"%DOCKER_COMPOSE%" version'
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
                withEnv(['DB_ENGINE=sqlite3']) {
                    echo 'Running Django tests...'
                    bat '.venv\\Scripts\\python.exe manage.py test'
                }
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
                withEnv(['DB_ENGINE=sqlite3']) {
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
                }

                echo 'Application startup checks passed.'
            }

            post {
                failure {
                    bat(returnStatus: true, script: 'if exist backend-test.log type backend-test.log')
                    bat(returnStatus: true, script: 'if exist frontend-test.log type frontend-test.log')
                }

                always {
                    echo 'Stopping temporary test servers...'

                    bat(returnStatus: true, script: '''
                    powershell -NoProfile -Command "$p=Get-NetTCPConnection -LocalPort 8100 -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique; if($p){Stop-Process -Id $p -Force -ErrorAction SilentlyContinue}"
                    powershell -NoProfile -Command "$p=Get-NetTCPConnection -LocalPort 4174 -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique; if($p){Stop-Process -Id $p -Force -ErrorAction SilentlyContinue}"
                    exit /b 0
                    ''')
                }
            }
        }

        stage('Build Docker backend image') {
            steps {
                echo 'Building Django Docker image...'
                bat '"%DOCKER%" build -t weblapt-backend:%IMAGE_TAG% -f Dockerfile .'
            }
        }

        stage('Build Docker nginx image') {
            steps {
                echo 'Building Nginx Docker image...'
                bat '"%DOCKER%" build -t weblapt-nginx:%IMAGE_TAG% -f nginx\\Dockerfile .'
            }
        }

        stage('Test Docker Compose deployment') {
            steps {
                withCredentials([string(credentialsId: 'weblapt-postgres-password', variable: 'POSTGRES_PASSWORD')]) {
                    withEnv([
                        'APP_PORT=8082',
                        'POSTGRES_HOST_PORT=5434',
                        "BACKEND_IMAGE=weblapt-backend:${env.IMAGE_TAG}",
                        "NGINX_IMAGE=weblapt-nginx:${env.IMAGE_TAG}"
                    ]) {
                        echo 'Validating Docker Compose configuration...'
                        bat '"%DOCKER_COMPOSE%" -p weblapt-ci config --quiet'

                        echo 'Starting CI PostgreSQL, Django and Nginx...'
                        bat '"%DOCKER_COMPOSE%" -p weblapt-ci up -d --no-build --wait --wait-timeout 120'

                        echo 'Checking test containers...'
                        bat '"%DOCKER_COMPOSE%" -p weblapt-ci ps'

                        echo 'Running Django tests against PostgreSQL...'
                        bat '"%DOCKER_COMPOSE%" -p weblapt-ci run --rm --no-deps backend python manage.py test'

                        echo 'Checking Vue frontend...'
                        bat 'curl.exe --fail --silent --show-error http://127.0.0.1:8082/ > NUL'

                        echo 'Checking Django API...'
                        bat 'curl.exe --fail --silent --show-error http://127.0.0.1:8082/api/auth/csrf/ > NUL'

                        echo 'Docker Compose integration tests passed.'
                    }
                }
            }

            post {
                failure {
                    withCredentials([string(credentialsId: 'weblapt-postgres-password', variable: 'POSTGRES_PASSWORD')]) {
                        withEnv([
                            'APP_PORT=8082',
                            'POSTGRES_HOST_PORT=5434',
                            "BACKEND_IMAGE=weblapt-backend:${env.IMAGE_TAG}",
                            "NGINX_IMAGE=weblapt-nginx:${env.IMAGE_TAG}"
                        ]) {
                            echo 'Showing CI container logs...'
                            bat(returnStatus: true, script: '"%DOCKER_COMPOSE%" -p weblapt-ci logs --tail 100')
                        }
                    }
                }

                always {
                    withCredentials([string(credentialsId: 'weblapt-postgres-password', variable: 'POSTGRES_PASSWORD')]) {
                        withEnv([
                            'APP_PORT=8082',
                            'POSTGRES_HOST_PORT=5434',
                            "BACKEND_IMAGE=weblapt-backend:${env.IMAGE_TAG}",
                            "NGINX_IMAGE=weblapt-nginx:${env.IMAGE_TAG}"
                        ]) {
                            echo 'Removing CI containers and temporary volumes...'
                            bat(returnStatus: true, script: '"%DOCKER_COMPOSE%" -p weblapt-ci down -v --remove-orphans')
                        }
                    }
                }
            }
        }

        stage('Push Docker images to Docker Hub') {
            when {
                branch 'main'
            }

            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'HUB_USER', passwordVariable: 'HUB_TOKEN')]) {
                    echo 'Logging in to Docker Hub...'

                    bat '''
                    @echo off
                    powershell -NoProfile -NonInteractive -Command "$env:HUB_TOKEN | & $env:DOCKER login --username $env:HUB_USER --password-stdin; exit $LASTEXITCODE"
                    '''

                    echo 'Tagging images for Docker Hub...'

                    bat '"%DOCKER%" tag weblapt-backend:%IMAGE_TAG% "%HUB_USER%/weblapt-backend:latest"'
                    bat '"%DOCKER%" tag weblapt-nginx:%IMAGE_TAG% "%HUB_USER%/weblapt-nginx:latest"'

                    bat '"%DOCKER%" tag weblapt-backend:%IMAGE_TAG% "%HUB_USER%/weblapt-backend:build-%BUILD_NUMBER%"'
                    bat '"%DOCKER%" tag weblapt-nginx:%IMAGE_TAG% "%HUB_USER%/weblapt-nginx:build-%BUILD_NUMBER%"'

                    echo 'Pushing backend image...'
                    bat '"%DOCKER%" push "%HUB_USER%/weblapt-backend:latest"'
                    bat '"%DOCKER%" push "%HUB_USER%/weblapt-backend:build-%BUILD_NUMBER%"'

                    echo 'Pushing Nginx image...'
                    bat '"%DOCKER%" push "%HUB_USER%/weblapt-nginx:latest"'
                    bat '"%DOCKER%" push "%HUB_USER%/weblapt-nginx:build-%BUILD_NUMBER%"'

                    echo 'Docker Hub publishing completed successfully.'
                }
            }

            post {
                always {
                    bat(returnStatus: true, script: '"%DOCKER%" logout')
                }
            }
        }

        stage('Deploy Docker application') {
            when {
                branch 'main'
            }

            steps {
                echo 'Preparing production images...'

                bat '"%DOCKER%" tag weblapt-backend:%IMAGE_TAG% weblapt-backend:latest'
                bat '"%DOCKER%" tag weblapt-nginx:%IMAGE_TAG% weblapt-nginx:latest'

                withCredentials([string(credentialsId: 'weblapt-postgres-password', variable: 'POSTGRES_PASSWORD')]) {
                    withEnv([
                        'APP_PORT=8081',
                        'POSTGRES_HOST_PORT=5433',
                        'BACKEND_IMAGE=weblapt-backend:latest',
                        'NGINX_IMAGE=weblapt-nginx:latest'
                    ]) {
                        echo 'Validating production Docker Compose...'
                        bat '"%DOCKER_COMPOSE%" -p weblapt config --quiet'

                        echo 'Ensuring production PostgreSQL is running...'
                        bat '"%DOCKER_COMPOSE%" -p weblapt up -d --no-build --wait --wait-timeout 120 postgres'

                        echo 'Updating Django and Nginx containers...'
                        bat '"%DOCKER_COMPOSE%" -p weblapt up -d --no-build --no-deps --force-recreate --wait --wait-timeout 120 backend nginx'

                        echo 'Checking production containers...'
                        bat '"%DOCKER_COMPOSE%" -p weblapt ps'

                        echo 'Checking production frontend...'
                        bat 'curl.exe --fail --silent --show-error http://127.0.0.1:8081/ > NUL'

                        echo 'Checking production Django API...'
                        bat 'curl.exe --fail --silent --show-error http://127.0.0.1:8081/api/auth/csrf/ > NUL'
                    }
                }

                echo 'Production deployment completed successfully.'
                echo 'Application: http://localhost:8081'
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully.'
        }

        failure {
            echo 'Pipeline failed. Check the failed stage and logs.'
        }
    }
}
