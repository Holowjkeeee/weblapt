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

        /*
         * Временная проверка.
         *
         * Используем отдельные порты, чтобы не мешать
         * уже развернутой production-версии.
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
         * Настоящий Deploy.
         * Выполняется только для main.
         */
        stage('Deploy and start application') {
            when {
                branch 'main'
            }

            steps {
                echo 'Deploying application from main branch...'

                /*
                 * Копирование проверенной версии.
                 */
                bat 'if not exist "%DEPLOY_DIR%" mkdir "%DEPLOY_DIR%"'

                bat '''
                robocopy . "%DEPLOY_DIR%" /E /XD .git .venv node_modules /XF db.sqlite3 backend-test.log frontend-test.log

                if %ERRORLEVEL% GEQ 8 exit /b %ERRORLEVEL%
                exit /b 0
                '''

                /*
                 * Python environment deployed application.
                 */
                bat '''
                if not exist "%DEPLOY_DIR%\\.venv\\Scripts\\python.exe" (
                    "%PYTHON%" -m venv "%DEPLOY_DIR%\\.venv"
                )
                '''

                bat '''
                "%DEPLOY_DIR%\\.venv\\Scripts\\python.exe" -m pip install --upgrade pip
                "%DEPLOY_DIR%\\.venv\\Scripts\\python.exe" -m pip install -r "%DEPLOY_DIR%\\requirements.txt"
                '''

                /*
                 * Database.
                 */
                bat '''
                "%DEPLOY_DIR%\\.venv\\Scripts\\python.exe" "%DEPLOY_DIR%\\manage.py" check
                "%DEPLOY_DIR%\\.venv\\Scripts\\python.exe" "%DEPLOY_DIR%\\manage.py" migrate
                '''

                /*
                 * Frontend dependencies are needed because Vite Preview
                 * will serve the already generated dist directory.
                 */
                bat '''
                cd /d "%DEPLOY_DIR%\\client"
                npm ci
                '''

                /*
                 * Check production build exists.
                 */
                bat '''
                if not exist "%DEPLOY_DIR%\\client\\dist\\index.html" (
                    echo Frontend dist was not found.
                    exit /b 1
                )
                '''

                /*
                 * Stop previous production version.
                 *
                 * Backend production  = 8001
                 * Frontend production = 4173
                 */
                bat '''
                powershell -NoProfile -Command "$p=Get-NetTCPConnection -LocalPort 8001 -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique; if($p){Stop-Process -Id $p -Force -ErrorAction SilentlyContinue}"

                powershell -NoProfile -Command "$p=Get-NetTCPConnection -LocalPort 4173 -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique; if($p){Stop-Process -Id $p -Force -ErrorAction SilentlyContinue}"

                exit /b 0
                '''

                /*
                 * Important:
                 * Jenkins must not kill these processes after Pipeline ends.
                 */
                withEnv(['JENKINS_NODE_COOKIE=weblapt-production']) {

                    echo 'Starting deployed Django backend...'

                    bat '''
                    powershell -NoProfile -Command "Start-Process -FilePath '%DEPLOY_DIR%\\.venv\\Scripts\\waitress-serve.exe' -ArgumentList '--listen=127.0.0.1:8001','app.wsgi:application' -WorkingDirectory '%DEPLOY_DIR%' -RedirectStandardOutput '%DEPLOY_DIR%\\backend-prod.log' -RedirectStandardError '%DEPLOY_DIR%\\backend-prod-error.log'"
                    '''

                    echo 'Starting deployed Vue frontend...'

                    bat '''
                    powershell -NoProfile -Command "Start-Process -FilePath 'cmd.exe' -ArgumentList '/c','npm run preview -- --host 127.0.0.1 --port 4173 > frontend-prod.log 2>&1' -WorkingDirectory '%DEPLOY_DIR%\\client'"
                    '''
                }

                /*
                 * Check deployed backend.
                 */
                bat '''
                powershell -NoProfile -Command "$limit=(Get-Date).AddSeconds(60); while((Get-Date) -lt $limit) { try { $r=Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:8001/api/auth/csrf/' -TimeoutSec 3; if ($r.StatusCode -eq 200) { Write-Host 'DEPLOYED BACKEND: SUCCESS'; exit 0 } } catch {}; Start-Sleep -Seconds 2 }; Write-Host 'DEPLOYED BACKEND: FAILED'; exit 1"
                '''

                /*
                 * Check deployed frontend.
                 */
                bat '''
                powershell -NoProfile -Command "$limit=(Get-Date).AddSeconds(60); while((Get-Date) -lt $limit) { try { $r=Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:4173/' -TimeoutSec 3; if ($r.StatusCode -eq 200) { Write-Host 'DEPLOYED FRONTEND: SUCCESS'; exit 0 } } catch {}; Start-Sleep -Seconds 2 }; Write-Host 'DEPLOYED FRONTEND: FAILED'; exit 1"
                '''

                /*
                 * Integration check:
                 * request comes to Vue server and is proxied to Django.
                 */
                bat '''
                curl.exe --fail --silent --show-error http://127.0.0.1:4173/api/auth/csrf/ > NUL
                '''

                echo 'Deployment completed successfully.'
                echo 'Application is running at http://127.0.0.1:4173'
            }
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