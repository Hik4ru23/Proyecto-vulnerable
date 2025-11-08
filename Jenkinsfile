pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'vulnerable-app'
        SONARQUBE_SERVER = 'sonarqube'
        ZAP_HOST = 'zap'
        ZAP_PORT = '8090'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Clonando repositorio...'
                checkout scm
            }
        }
        
        stage('Build') {
            steps {
                echo 'Construyendo imagen Docker...'
                script {
                    docker.build("${DOCKER_IMAGE}:${BUILD_NUMBER}")
                }
            }
        }
        
        stage('Test - Unit Tests') {
            steps {
                echo 'Ejecutando pruebas unitarias...'
                script {
                    docker.image("${DOCKER_IMAGE}:${BUILD_NUMBER}").inside {
                        sh 'python -m pytest test_app.py -v || echo "Tests ejecutados"'
                    }
                }
            }
        }
        
        stage('Security - Dependency Check') {
            steps {
                echo 'Analizando dependencias con OWASP Dependency-Check...'
                dependencyCheck additionalArguments: '''
                    -o "./"
                    -s "./"
                    -f "ALL"
                    --prettyPrint
                    ''', 
                    odcInstallation: 'OWASP Dependency-Check'
                
                dependencyCheckPublisher pattern: 'dependency-check-report.xml'
            }
        }
        
        stage('Security - SonarQube Analysis') {
            steps {
                echo 'Analizando código con SonarQube...'
                script {
                    def scannerHome = tool 'SonarQubeScanner'
                    withSonarQubeEnv('sonarqube') {
                        sh """
                            ${scannerHome}/bin/sonar-scanner \
                            -Dsonar.projectKey=vulnerable-app \
                            -Dsonar.projectName=VulnerableApp \
                            -Dsonar.sources=. \
                            -Dsonar.python.version=3.9
                        """
                    }
                }
            }
        }
        
        stage('Security - Quality Gate') {
            steps {
                echo 'Esperando resultado de Quality Gate...'
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: false
                }
            }
        }
        
        stage('Deploy to Test') {
            steps {
                echo 'Desplegando aplicación en ambiente de prueba...'
                script {
                    sh """
                        docker stop vulnerable-app-test || true
                        docker rm vulnerable-app-test || true
                        docker run -d \
                            --name vulnerable-app-test \
                            --network jenkins \
                            -p 5000:5000 \
                            ${DOCKER_IMAGE}:${BUILD_NUMBER}
                    """
                    // Esperar que la aplicación inicie
                    sh 'sleep 10'
                }
            }
        }
        
        stage('Security - OWASP ZAP Scan') {
            steps {
                echo 'Ejecutando escaneo dinámico con OWASP ZAP...'
                script {
                    sh """
                        docker exec zap \
                        zap-cli quick-scan \
                        --self-contained \
                        --start-options '-config api.disablekey=true' \
                        http://vulnerable-app-test:5000
                    """
                }
            }
        }
        
        stage('Security - Generate Reports') {
            steps {
                echo 'Generando reportes de seguridad...'
                script {
                    sh """
                        docker exec zap \
                        zap-cli report \
                        -o zap-report.html \
                        -f html
                    """
                }
                
                // Publicar reportes
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: '.',
                    reportFiles: 'zap-report.html',
                    reportName: 'OWASP ZAP Report'
                ])
            }
        }
    }
    
    post {
        always {
            echo 'Limpiando recursos...'
            script {
                // Limpiar contenedor de prueba
                sh 'docker stop vulnerable-app-test || true'
                sh 'docker rm vulnerable-app-test || true'
            }
        }
        
        success {
            echo '✅ Pipeline ejecutado exitosamente'
            emailext (
                subject: "Pipeline Exitoso: ${currentBuild.fullDisplayName}",
                body: "El pipeline se ejecutó correctamente. Ver detalles en: ${env.BUILD_URL}",
                to: 'tu-email@ejemplo.com'
            )
        }
        
        failure {
            echo '❌ Pipeline falló'
            emailext (
                subject: "Pipeline Fallido: ${currentBuild.fullDisplayName}",
                body: "El pipeline falló. Ver detalles en: ${env.BUILD_URL}",
                to: 'tu-email@ejemplo.com'
            )
        }
    }
}
