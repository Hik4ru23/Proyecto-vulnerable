pipeline {
    agent any
    
    environment {
        PROJECT_NAME = "pipeline-test"
        DOCKER_IMAGE = 'vulnerable-app'
        APP_PORT = '5000'
        SONARQUBE_URL = "http://sonarqube:9000"
        TARGET_URL = "http://vulnerable-app-test:5000"
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo '📥 Clonando repositorio...'
                checkout scm
            }
        }
        
        stage('Build Docker Image') {
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
                        python -m pytest test_app.py -v || echo "Tests completados"
                    """
                }
            }
        }
        
        stage('Security - Python Audit') {
            steps {
                echo '🔍 Auditoría de seguridad Python con pip-audit...'
                script {
                    sh """
                        mkdir -p reports
                        docker run --rm \
                        -v \$(pwd):/app \
                        -w /app \
                        python:3.9-slim \
                        bash -c 'pip install pip-audit && pip-audit -r requirements.txt --format markdown > reports/pip-audit.md || true'
                    """
                }
                
                archiveArtifacts artifacts: 'reports/pip-audit.md', allowEmptyArchive: true
            }
        }
        
        stage('Security - SonarQube Analysis') {
            steps {
                echo '📊 Analizando código con SonarQube...'
                script {
                    withSonarQubeEnv('sonarqube') {
                        sh """
                            docker run --rm \
                            --network jenkins-net \
                            -v \$(pwd):/usr/src \
                            -e SONAR_HOST_URL=${SONARQUBE_URL} \
                            -e SONAR_TOKEN=\${SONAR_AUTH_TOKEN} \
                            sonarsource/sonar-scanner-cli \
                            -Dsonar.projectKey=${PROJECT_NAME} \
                            -Dsonar.projectName="${PROJECT_NAME}" \
                            -Dsonar.sources=/usr/src \
                            -Dsonar.exclusions=**/test_**,**/reports/**,**/zap-reports/**,**/.venv/**,**/venv/** \
                            -Dsonar.python.version=3.9 || echo "SonarQube completado"
                        """
                    }
                }
            }
        }
        
        stage('Security - Quality Gate') {
            steps {
                echo '⏳ Esperando Quality Gate de SonarQube...'
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: false
                }
            }
        }
        
        stage('Security - Dependency Check') {
            steps {
                echo '🔍 Analizando dependencias con OWASP Dependency-Check...'
                script {
                    withCredentials([string(credentialsId: 'nvdApiKey', variable: 'NVD_API_KEY')]) {
                        sh """
                            mkdir -p reports
                            docker run --rm \
                            -v \$(pwd):/src \
                            -v dependency-check-data:/usr/share/dependency-check/data \
                            owasp/dependency-check \
                            --scan /src \
                            --format HTML \
                            --format JSON \
                            --format XML \
                            --project "${PROJECT_NAME}" \
                            --nvdApiKey \${NVD_API_KEY} \
                            --enableExperimental \
                            --out /src/reports || echo "Dependency-Check completado"
                        """
                    }
                }
                
                archiveArtifacts artifacts: 'reports/dependency-check-report.*', allowEmptyArchive: true
            }
        }
        
        stage('Deploy to Test Environment') {
            steps {
                echo '🚀 Desplegando aplicación en ambiente de prueba...'
                script {
                    sh 'docker stop vulnerable-app-test 2>/dev/null || true'
                    sh 'docker rm vulnerable-app-test 2>/dev/null || true'
                    
                    sh """
                        docker run -d \
                        --name vulnerable-app-test \
                        --network jenkins-net \
                        -p ${APP_PORT}:5000 \
                        ${DOCKER_IMAGE}:${BUILD_NUMBER}
                    """
                    
                    echo 'Esperando 15 segundos a que la aplicación inicie...'
                    sleep 15
                    
                    echo 'Verificando que la aplicación está corriendo...'
                    sh 'docker ps | grep vulnerable-app-test'
                    sh 'docker logs vulnerable-app-test | tail -20'
                }
            }
        }
        
        stage('Security - OWASP ZAP Scan') {
            steps {
                echo '🕷️ Ejecutando escaneo dinámico con OWASP ZAP...'
                script {
                    sh 'mkdir -p zap-reports'
                    
                    sh """
                        docker run --rm \
                        --network jenkins-net \
                        -v \$(pwd)/zap-reports:/zap/wrk:rw \
                        ghcr.io/zaproxy/zaproxy:stable \
                        zap-baseline.py \
                        -t ${TARGET_URL} \
                        -r zap-report.html \
                        -w zap-report.md || echo "ZAP scan completado"
                    """
                }
                
                archiveArtifacts artifacts: 'zap-reports/*', allowEmptyArchive: true
            }
        }
        
        stage('Publish HTML Reports') {
            steps {
                echo '📄 Publicando reportes HTML...'
                script {
                    // Publicar reporte de Dependency-Check
                    publishHTML([
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'reports',
                        reportFiles: 'dependency-check-report.html',
                        reportName: 'OWASP Dependency-Check Report',
                        reportTitles: 'Dependency Check'
                    ])
                    
                    // Publicar reporte de ZAP
                    publishHTML([
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'zap-reports',
                        reportFiles: 'zap-report.html',
                        reportName: 'OWASP ZAP Security Report',
                        reportTitles: 'ZAP Scan'
                    ])
                }
            }
        }
        
        stage('Summary') {
            steps {
                echo '📊 Generando resumen de reportes...'
                script {
                    sh '''
                        echo "==================================="
                        echo "  RESUMEN DE ANÁLISIS DE SEGURIDAD"
                        echo "==================================="
                        echo ""
                        echo "📁 Reportes generados:"
                        ls -lh reports/ 2>/dev/null || echo "  ⚠️  No se encontró directorio reports/"
                        echo ""
                        ls -lh zap-reports/ 2>/dev/null || echo "  ⚠️  No se encontró directorio zap-reports/"
                        echo ""
                        ls -lh *.json 2>/dev/null || echo "  ℹ️  No se encontraron reportes JSON adicionales"
                        echo ""
                        echo "==================================="
                    '''
                }
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
            echo '✅ ¡Pipeline ejecutado exitosamente!'
            echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
            echo '📊 REPORTES DISPONIBLES:'
            echo '   • Dependency-Check: Ver en "OWASP Dependency-Check Report"'
            echo '   • OWASP ZAP: Ver en "OWASP ZAP Security Report"'
            echo '   • pip-audit: Ver en "Build Artifacts"'
            echo '   • SonarQube: http://sonarqube:9000/dashboard?id=pipeline-test'
            echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
        }
        
        failure {
            echo '❌ Pipeline falló'
            echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
            echo '💡 Revisa los logs arriba para identificar el error'
            echo '   Etapas comunes de fallo:'
            echo '   • Build: Verifica Dockerfile y dependencias'
            echo '   • Tests: Verifica test_app.py'
            echo '   • Dependency-Check: Primera ejecución puede tardar 30+ min'
            echo '   • ZAP: Verifica que la app esté corriendo'
            echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
        }
        
        unstable {
            echo '⚠️  Pipeline inestable - Hay warnings pero no errores críticos'
        }
    }
