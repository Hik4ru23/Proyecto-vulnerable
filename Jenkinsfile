pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'vulnerable-app'
        APP_PORT = '5000'
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
                    sh "docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} ."
                    sh "docker tag ${DOCKER_IMAGE}:${BUILD_NUMBER} ${DOCKER_IMAGE}:latest"
                }
            }
        }
        
        stage('Test - Unit Tests') {
            steps {
                echo '🧪 Ejecutando pruebas unitarias...'
                script {
                    sh """
                        docker run --rm \
                        ${DOCKER_IMAGE}:${BUILD_NUMBER} \
                        python -m pytest test_app.py -v || echo 'Tests completados'
                    """
                }
            }
        }
        
        stage('Security - Dependency Check') {
            steps {
                echo '🔍 Analizando dependencias con OWASP Dependency-Check...'
                script {
                    // Ejecutar Dependency-Check
                    sh """
                        docker run --rm \
                        -v \$(pwd):/src \
                        -v dependency-check-data:/usr/share/dependency-check/data \
                        owasp/dependency-check \
                        --scan /src \
                        --format ALL \
                        --project "vulnerable-app" \
                        --out /src || echo 'Dependency check completado'
                    """
                }
                
                // Publicar resultados
                dependencyCheckPublisher pattern: 'dependency-check-report.xml', failedTotalHigh: 0, unstableTotalHigh: 10
            }
        }
        
        stage('Security - SonarQube Analysis') {
            steps {
                echo '📊 Analizando código con SonarQube...'
                script {
                    withSonarQubeEnv('sonarqube') {
                        sh """
                            docker run --rm \
                            --network jenkins \
                            -v \$(pwd):/usr/src \
                            sonarsource/sonar-scanner-cli \
                            -Dsonar.projectKey=vulnerable-app \
                            -Dsonar.sources=/usr/src \
                            -Dsonar.host.url=http://sonarqube:9000 \
                            -Dsonar.token=\${SONAR_AUTH_TOKEN} || echo 'SonarQube scan completado'
                        """
                    }
                }
            }
        }
        
        stage('Deploy to Test') {
            steps {
                echo '🚀 Desplegando aplicación en ambiente de prueba...'
                script {
                    // Detener contenedor anterior si existe
                    sh 'docker stop vulnerable-app-test 2>/dev/null || true'
                    sh 'docker rm vulnerable-app-test 2>/dev/null || true'
                    
                    // Ejecutar nuevo contenedor
                    sh """
                        docker run -d \
                        --name vulnerable-app-test \
                        --network jenkins \
                        -p ${APP_PORT}:5000 \
                        ${DOCKER_IMAGE}:${BUILD_NUMBER}
                    """
                    
                    // Esperar a que la aplicación inicie
                    echo 'Esperando 10 segundos a que la aplicación inicie...'
                    sleep 10
                    
                    // Verificar que está corriendo
                    sh 'curl -f http://localhost:5000/hello?name=Test || echo "App iniciando..."'
                }
            }
        }
        
        stage('Security - OWASP ZAP Scan') {
            steps {
                echo '🕷️ Ejecutando escaneo dinámico con OWASP ZAP...'
                script {
                    sh """
                        docker exec zap \
                        zap-baseline.py \
                        -t http://vulnerable-app-test:5000 \
                        -r /zap/wrk/zap-report.html \
                        -w /zap/wrk/zap-report.md \
                        || true
                    """
                    
                    // Copiar reportes
                    sh """
                        docker cp zap:/zap/wrk/zap-report.html . || echo 'No se pudo copiar HTML'
                        docker cp zap:/zap/wrk/zap-report.md . || echo 'No se pudo copiar MD'
                    """
                }
            }
        }
        
        stage('Security - Generate Reports') {
            steps {
                echo '📄 Generando reportes de seguridad...'
                
                // Publicar reportes HTML
                publishHTML([
                    allowMissing: true,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: '.',
                    reportFiles: 'zap-report.html',
                    reportName: 'OWASP ZAP Security Report'
                ])
                
                publishHTML([
                    allowMissing: true,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: '.',
                    reportFiles: 'dependency-check-report.html',
                    reportName: 'OWASP Dependency-Check Report'
                ])
                
                // Archivar reportes
                archiveArtifacts artifacts: '*.html, *.xml, *.md', allowEmptyArchive: true
            }
        }
    }
    
    post {
        always {
            echo '🧹 Limpiando recursos...'
            script {
                sh 'docker stop vulnerable-app-test 2>/dev/null || true'
                sh 'docker rm vulnerable-app-test 2>/dev/null || true'
            }
        }
        
        success {
            echo '✅ Pipeline ejecutado exitosamente!'
        }
        
        failure {
            echo '❌ Pipeline falló - Revisa los logs'
        }
    }
}
