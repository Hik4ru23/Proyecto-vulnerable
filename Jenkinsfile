pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'vulnerable-app'
        APP_PORT = '5000'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo '📦 Clonando repositorio...'
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
        
        // Esta etapa de Test no la incluiste en tu código vulnerable,
        // así que la comentaré. Si tienes 'test_app.py', descoméntala.
        /*
        stage('Test - Unit Tests') {
            steps {
                echo '🧪 Ejecutando pruebas unitarias...'
                script {
                    sh """
                        docker run --rm \
                        ${DOCKER_IMAGE}:${BUILD_NUMBER} \
                        python -m pytest test_app.py -v
                    """
                }
            }
        }
        */
        
        stage('Security - Dependency Check') {
            steps {
                echo '🔍 Analizando dependencias con OWASP Dependency-Check...'
                script {
                    // ¡ARREGLO! Se añade '--user root' para solucionar el
                    // error de permisos "unable to create the output directory".
                    sh """
                        docker run --rm \
                        --user root \
                        -v \$(pwd):/src \
                        -v dependency-check-data:/usr/share/dependency-check/data \
                        owasp/dependency-check \
                        --scan /src \
                        --format HTML \
                        --format JSON \
                        --project "vulnerable-app" \
                        --out /src/reports || true
                    """
                }
                
                // Archivar reportes
                archiveArtifacts artifacts: 'reports/dependency-check-report.*', allowEmptyArchive: true
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
                    echo '⏳ Esperando 15 segundos a que la aplicación inicie...'
                    sleep 15
                    
                    // Verificar que está corriendo
                    sh 'docker ps | grep vulnerable-app-test'
                    sh 'docker logs vulnerable-app-test'
                }
            }
        }
        
        stage('Security - OWASP ZAP Scan') {
            steps {
                echo '🕷️ Ejecutando escaneo dinámico con OWASP ZAP...'
                script {
                    // Crear directorio para reportes
                    sh 'mkdir -p zap-reports'
                    
                    // ¡ARREGLO! Se añade '--user root' para que ZAP
                    // pueda escribir el reporte en la carpeta de Jenkins.
                    sh """
                        docker run --rm \
                        --user root \
                        --network jenkins \
                        -v \$(pwd)/zap-reports:/zap/wrk:rw \
                        ghcr.io/zaproxy/zaproxy:stable \
                        zap-baseline.py \
                        -t http://vulnerable-app-test:5000 \
                        -r zap-report.html \
                        -w zap-report.md || true
                    """
                }
                
                // Archivar reportes
                archiveArtifacts artifacts: 'zap-reports/*', allowEmptyArchive: true
            }
        }
        
        stage('Generate Reports') {
            steps {
                echo '📊 Reportes generados y archivados'
                script {
                    // Listar reportes generados
                    sh 'ls -la reports/ || echo "No reports directory"'
                    sh 'ls -la zap-reports/ || echo "No zap-reports directory"'
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
            echo '✅ Pipeline ejecutado exitosamente!'
            echo 'Revisa los reportes en la sección "Build Artifacts"'
        }
        
        failure {
            echo '❌ Pipeline falló - Revisa los logs arriba'
        }
    }
}
