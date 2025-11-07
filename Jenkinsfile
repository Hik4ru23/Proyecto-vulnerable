pipeline {
    // 1. CONFIGURACIÓN DEL AGENTE
    // Prepara la herramienta JDK 'jenkins-java' que configuraste en la UI.
    agent {
        any {
            tools {
                jdk 'jenkins-java'
            }
        }
    }
    
    // ¡CAMBIO! Se eliminó el bloque 'environment' que usaba la API Key.
    // Ya no es necesario.

    stages {

        // 2. ETAPA DE CONSTRUCCIÓN
        // ¡CAMBIO! Ahora también instala 'python3-yaml' para ZAP.
        stage('Build') {
            steps {
                echo '📦 Actualizando e instalando Python y herramientas...'
                sh 'apt-get update'
                sh 'apt-get install -y python3 python3-pip unzip curl python3-yaml' // Se añadió 'python3-yaml'
                
                echo '🐍 Instalando dependencias de Python...'
                sh 'pip3 install --break-system-packages -r requirements.txt'
            }
        }

        // 3. ETAPA DE ANÁLISIS ESTÁTICO (SAST)
        // Analiza tu código con SonarQube
        stage('Analyze - SonarQube (SAST)') {
            steps {
                script {
                    def scannerHome = tool 'SonarScanner-Default' 
                    withSonarQubeEnv('MiSonarQubeServer') { 
                        sh "${scannerHome}/bin/sonar-scanner -Dsonar.projectName=Proyecto-Python-Vulnerable -Dsonar.projectKey=py-vulnerable -Dsonar.sources=."
                    }
                }
            }
        }

        // 4. ETAPA DE ANÁLISIS DE DEPENDENCIAS (SCA)
        // ¡CAMBIO! Se eliminó la API Key. Ahora usará el feed anónimo.
        stage('Dependency Check') {
            steps {
                echo '🔍 Instalando y ejecutando Dependency-Check...'
                sh '''
                    set -e
                    echo "➡️ Descargando Dependency-Check..."
                    if [ ! -f dependency-check-9.2.0-release.zip ]; then
                        wget -q https://github.com/jeremylong/DependencyCheck/releases/download/v9.2.0/dependency-check-9.2.0-release.zip
                    fi

                    echo "➡️ Descomprimiendo sin pedir confirmación..."
                    unzip -o -q dependency-check-9.2.0-release.zip
                    chmod +x dependency-check/bin/dependency-check.sh

                    echo "🚀 Ejecutando análisis..."
                    # Se quitó --nvdApiKey.
                    # Esto TARDARÁ (20-30 min) la primera vez mientras descarga la BD.
                    ./dependency-check/bin/dependency-check.sh \
                        --project "Proyecto-Vulnerable" \
                        --scan . \
                        --format HTML \
                        --out dependency-check-report.html \
                        --nvdApiDelay 4000
                '''
            }
            post {
                success {
                    echo '✅ Dependency-Check finalizado correctamente.'
                    archiveArtifacts artifacts: 'dependency-check-report.html', allowEmptyArchive: true

                    // 📊 Mostrar el reporte HTML en Jenkins (requiere plugin 'HTML Publisher')
                    publishHTML(target: [
                        allowMissing: true,
                        keepAll: true,
                        reportDir: '.',
                        reportFiles: 'dependency-check-report.html',
                        reportName: '🔒 Dependency-Check Report'
                    ])
                }
                failure {
                    echo '❌ Dependency-Check falló.'
                }
                always {
                    echo '🧹 Limpiando workspace de DC...'
                    sh 'rm -rf dependency-check dependency-check-9.2.0-release.zip'
                }
            }
        }

        // 5. ETAPA DE DESPLIEGUE (A PRUEBAS)
        stage('Deploy (to Test Environment)') {
            steps {
                echo '🚀 Desplegando app en segundo plano...'
                sh 'nohup python3 vulnerable.py &' 
                sleep 20 // 20 segundos para asegurar que la app inicie
                echo '✅ App iniciada en http://jenkins-lts:5000'
            }
        }

        // 6. ETAPA DE ANÁLISIS DINÁMICO (DAST)
        // Se ejecuta con 'python3' (que ahora tiene 'yaml')
        stage('Security Test (Dynamic) - OWASP ZAP (DAST)') {
            steps {
                echo '🧨 Ejecutando análisis dinámico con OWASP ZAP...'
                sh '''
                    if [ ! -f zap-baseline.py ]; then
                        echo "⬇️ Descargando OWASP ZAP baseline..."
                        curl -O https://raw.githubusercontent.com/zaproxy/zaproxy/main/docker/zap-baseline.py
                        chmod +x zap-baseline.py
                    fi

                    echo "🚀 Iniciando análisis con OWASP ZAP..."
                    # Esto ahora funcionará gracias a 'python3-yaml'
                    python3 ./zap-baseline.py \
                        -t http://jenkins-lts:5000/hello?name=test \
                        -H zap \
                        -p 8090 \
                        -r zap-report.html
                '''
            }
            post {
                always {
                    echo '📑 Archivando reporte de OWASP ZAP...'
                    archiveArtifacts artifacts: 'zap-report.html', allowEmptyArchive: true

                    // 📊 Publicar el reporte HTML en Jenkins (requiere plugin 'HTML Publisher')
                    publishHTML(target: [
                        allowMissing: true,
                        keepAll: true,
                        reportDir: '.',
                        reportFiles: 'zap-report.html',
                        reportName: '🕷 OWASP ZAP Report'
                    ])
                }
            }
        }
    } // Fin de 'stages'

    // 7. ETAPA DE LIMPIEZA
    post { 
        always {
            echo '🧽 Pipeline finalizado. Limpiando entorno...'
            // Detiene el servidor de Python
            sh 'pkill -f "python3 vulnerable.py" || true'
            echo 'Cleanup complete.'
        }
    }
}
