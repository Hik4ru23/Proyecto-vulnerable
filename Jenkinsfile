# Crear/actualizar Jenkinsfile
@"
pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'vulnerable-app'
        SONAR_PROJECT_KEY = 'vulnerable-app'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo '📥 Clonando repositorio...'
                checkout scm
            }
        }
        
        stage('Build') {
            steps {
                echo '🔨 Construyendo imagen Docker...'
                script {
                    bat 'docker build -t %DOCKER_IMAGE%:latest .'
                }
            }
        }
        
        stage('Test') {
            steps {
                echo '🧪 Verificando sintaxis de Python...'
                script {
                    bat '''
                        python -m py_compile vulnerable.py
                        echo Sintaxis verificada correctamente
                    '''
                }
            }
        }
        
        stage('OWASP Dependency-Check') {
            steps {
                echo '🔍 Analizando dependencias con OWASP Dependency-Check...'
                dependencyCheck additionalArguments: '''
                    --scan .
                    --format HTML
                    --format XML
                    --project vulnerable-app
                ''', odcInstallation: 'dependency-check'
                
                dependencyCheckPublisher pattern: 'dependency-check-report.xml'
            }
        }
        
        stage('SonarQube Analysis') {
            steps {
                echo '📊 Analizando código con SonarQube...'
                script {
                    def scannerHome = tool 'sonarqube-scanner'
                    withSonarQubeEnv('sonarqube') {
                        bat \"\"\"%scannerHome%\\bin\\sonar-scanner.bat -Dsonar.projectKey=%SONAR_PROJECT_KEY% -Dsonar.sources=. -Dsonar.host.url=http://sonarqube:9000 -Dsonar.python.version=3.9\"\"\"
                    }
                }
            }
        }
        
        stage('SonarQube Quality Gate') {
            steps {
                echo '⏳ Esperando resultado del Quality Gate...'
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: false
                }
            }
        }
        
        stage('Deploy to Test') {
            steps {
                echo '🚀 Desplegando aplicación en entorno de prueba...'
                script {
                    bat '''
                        docker stop vulnerable-app-test 2>nul || echo No hay contenedor previo
                        docker rm vulnerable-app-test 2>nul || echo No hay contenedor para eliminar
                    '''
                    
                    bat 'docker run -d --name vulnerable-app-test --network jenkins -p 5000:5000 %DOCKER_IMAGE%:latest'
                    
                    echo 'Esperando 15 segundos a que la aplicación inicie...'
                    sleep 15
                }
            }
        }
        
        stage('OWASP ZAP Scan') {
            steps {
                echo '🛡️ Ejecutando escaneo dinámico con OWASP ZAP...'
                script {
                    bat '''
                        docker exec zap zap-baseline.py -t http://vulnerable-app-test:5000 -r zap-report.html -J zap-report.json || echo ZAP scan completado con advertencias
                    '''
                    
                    bat 'docker cp zap:/zap/wrk/zap-report.html . || echo No se pudo copiar el reporte ZAP'
                }
            }
        }
    }
    
    post {
        always {
            echo '📦 Archivando reportes...'
            archiveArtifacts artifacts: '**/dependency-check-report.html, **/zap-report.html', allowEmptyArchive: true
            
            echo '📄 Publicando reportes HTML...'
            publishHTML([
                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: '.',
                reportFiles: 'dependency-check-report.html',
                reportName: 'Dependency-Check Report'
            ])
            
            publishHTML([
                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: '.',
                reportFiles: 'zap-report.html',
                reportName: 'OWASP ZAP Report'
            ])
        }
        
        success {
            echo '✅ Pipeline ejecutado exitosamente!'
        }
        
        failure {
            echo '❌ Pipeline falló. Revisa los logs para más detalles.'
        }
    }
}
"@ | Out-File -FilePath Jenkinsfile -Encoding UTF8 -NoNewline
