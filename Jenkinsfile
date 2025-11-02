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
                    sh 'docker build -t $DOCKER_IMAGE:latest .'
                }
            }
        }
        
        stage('Test') {
            steps {
                echo '🧪 Ejecutando pruebas unitarias...'
                script {
                    sh '''
                        python3 -m pip install --upgrade pip
                        pip3 install -r requirements.txt
                        pip3 install pytest
                        python3 -m pytest test_vulnerable.py --verbose || echo "Tests completed"
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
                    --failOnCVSS 7
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
                        sh """
                            ${scannerHome}/bin/sonar-scanner \
                            -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                            -Dsonar.sources=. \
                            -Dsonar.host.url=http://sonarqube:9000 \
                            -Dsonar.python.version=3.9
                        """
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
                    // Detener contenedor anterior si existe
                    sh '''
                        docker stop vulnerable-app-test 2>/dev/null || echo "No container to stop"
                        docker rm vulnerable-app-test 2>/dev/null || echo "No container to remove"
                    '''
                    
                    // Ejecutar nuevo contenedor
                    sh 'docker run -d --name vulnerable-app-test --network jenkins -p 5000:5000 $DOCKER_IMAGE:latest'
                    
                    echo 'Esperando a que la aplicación inicie...'
                    sleep 10
                }
            }
        }
        
        stage('OWASP ZAP Scan') {
            steps {
                echo '🛡️ Ejecutando escaneo dinámico con OWASP ZAP...'
                script {
                    sh '''
                        docker exec zap zap-baseline.py \
                        -t http://vulnerable-app-test:5000 \
                        -r zap-report.html \
                        -J zap-report.json \
                        || echo "ZAP scan completed with warnings"
                    '''
                    
                    // Copiar reporte
                    sh 'docker cp zap:/zap/wrk/zap-report.html . || echo "Could not copy ZAP report"'
                }
            }
        }
    }
    
    post {
        always {
            echo '📦 Archivando reportes...'
            archiveArtifacts artifacts: '**/dependency-check-report.html, **/zap-report.html', allowEmptyArchive: true
            
            echo '📄 Publicando reportes de pruebas...'
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
```

### Archivo: `.gitignore`
```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv
*.log
.DS_Store
dependency-check-report.*
zap-report.*
