pipeline {
    agent any

    environment {
        // Credencial tipo "Secret text" o "Username/Password" si la guardas así en Jenkins
        NVD_API_KEY = credentials('NVD_API_KEY')
        DC_DATA_DIR = "${env.WORKSPACE}/dependency-check-data" // Persistencia local dentro del workspace (puedes cambiar)
    }

    options {
        // Timeouts razonables para evitar builds eternos
        timeout(time: 40, unit: 'MINUTES')
        // Mantener solo artefactos recientes
    }

    stages {
        stage('Checkout') {
            steps {
                echo '📦 Descargando código...'
                git branch: 'main', url: 'https://github.com/Hik4ru23/Proyecto-vulnerable.git'
            }
        }

        stage('Dependency Check - Static') {
            steps {
                echo '🔍 Ejecutando OWASP Dependency-Check (contenedor)...'
                script {
                    // Asegurarse de tener el directorio para la DB
                    sh """
                        set -e
                        mkdir -p "${DC_DATA_DIR}"
                        # permiso seguro
                        chmod 700 "${DC_DATA_DIR}" || true
                    """

                    // Ejecutar dependency-check en docker para evitar problemas de binarios locales
                    sh """
                        set -e
                        docker run --rm \\
                          -v "${env.WORKSPACE}":/src \\
                          -v "${DC_DATA_DIR}":/usr/share/dependency-check/data \\
                          -e "NVD_API_KEY=${NVD_API_KEY}" \\
                          owasp/dependency-check:9.2.0 \\
                          --project "Proyecto-Vulnerable" \\
                          --scan /src \\
                          --format HTML \\
                          --out /src/dependency-check-report.html \\
                          --nvdApiKey "${NVD_API_KEY}" \\
                          --nvdApiDelay 4000 || true
                    """
                }
            }
            post {
                success {
                    echo '✅ Dependency-Check completado (success).'
                }
                unstable {
                    echo '⚠️ Dependency-Check terminó con advertencias/unstable.'
                }
                failure {
                    echo '❌ Dependency-Check falló. Se intentará regenerar DB y reintentar...'
                    // Intento de recuperación: eliminar DB corrupta y reintentar (one-shot)
                    sh """
                        set -e || true
                        echo "🔁 Eliminando DB local de dependency-check para regenerar..."
                        rm -rf "${DC_DATA_DIR}" || true
                        mkdir -p "${DC_DATA_DIR}"
                        docker run --rm \\
                          -v "${env.WORKSPACE}":/src \\
                          -v "${DC_DATA_DIR}":/usr/share/dependency-check/data \\
                          -e "NVD_API_KEY=${NVD_API_KEY}" \\
                          owasp/dependency-check:9.2.0 \\
                          --project "Proyecto-Vulnerable" \\
                          --scan /src \\
                          --format HTML \\
                          --out /src/dependency-check-report.html \\
                          --nvdApiKey "${NVD_API_KEY}" \\
                          --nvdApiDelay 4000 || true
                    """
                }
                always {
                    archiveArtifacts artifacts: 'dependency-check-report.html', allowEmptyArchive: true
                    publishHTML(target: [
                        allowMissing: true,
                        keepAll: true,
                        reportDir: '.',
                        reportFiles: 'dependency-check-report.html',
                        reportName: '🔒 Dependency-Check Report'
                    ])
                }
            }
        }

        stage('Start Target App (for DAST)') {
            steps {
                echo '🚀 Iniciando app vulnerable (si aplica) para escaneo...'
                // Si tu app se inicia con python vulnerable.py, levantamos en background dentro del workspace
                sh '''
                    # intenta iniciar la app si existe; si no, lo ignoramos
                    if [ -f vulnerable.py ]; then
                        nohup python3 vulnerable.py > vulnerable.log 2>&1 & echo $! > vulnerable.pid || true
                        sleep 2
                        echo "✅ App vulnerable iniciada (si existía)."
                    else
                        echo "ℹ️ vulnerable.py no encontrado — omitiendo levantado del target."
                    fi
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'vulnerable.log', allowEmptyArchive: true
                }
            }
        }

        stage('Security Test (Dynamic) - OWASP ZAP (DAST)') {
            steps {
                echo '🧨 Ejecutando análisis dinámico con OWASP ZAP (contenedor)...'
                script {
                    // URL objetivo: si corres la app en el mismo jenkins, ajusta host/puerto a donde responde la app
                    def targetUrl = "http://localhost:5000/hello?name=test"

                    // Bajamos zap-baseline.py si no existe
                    sh '''
                        set -e
                        if [ ! -f zap-baseline.py ]; then
                            echo "⬇️ Descargando zap-baseline.py..."
                            curl -sSf -O https://raw.githubusercontent.com/zaproxy/zaproxy/main/docker/zap-baseline.py
                            chmod +x zap-baseline.py
                        fi
                    '''

                    // Ejecutar ZAP en un contenedor en modo daemon y ejecutar zap-baseline.py apuntando al demonio
                    sh """
                        set -e
                        ZAP_CONTAINER_NAME=jenkins-zap-\$(date +%s)
                        docker run -u zap --name "\$ZAP_CONTAINER_NAME" -d -p 8090:8090 -p 8080:8080 owasp/zap2docker-stable zap.sh -daemon -host 0.0.0.0 -port 8090 -config api.disablekey=true
                        echo "🟢 Esperando que ZAP inicie..."
                        sleep 8

                        # Ejecutar el script baseline desde host, apuntando al daemon
                        python3 zap-baseline.py -t "${targetUrl}" -r zap-report.html -z "-config api.key= -daemon" -p 8090 || echo "⚠️ OWASP ZAP finalizó con advertencias."

                        # Copiar report (ya queda en workspace si se ejecutó desde aquí)
                        docker stop \$ZAP_CONTAINER_NAME || true
                        docker rm \$ZAP_CONTAINER_NAME || true
                    """
                }
            }
            post {
                always {
                    echo '📑 Archivando reporte de OWASP ZAP...'
                    archiveArtifacts artifacts: 'zap-report.html', allowEmptyArchive: true
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
    }

    post {
        always {
            echo '🧽 Pipeline finalizado. Limpieza final...'
            // matar procesos locales si se levantó la app
            sh '''
                set -e || true
                if [ -f vulnerable.pid ]; then
                    PID=$(cat vulnerable.pid || echo "")
                    if [ -n "$PID" ]; then
                        kill $PID || true
                        rm -f vulnerable.pid
                    fi
                fi
                # borrar contenedores huérfanos de ZAP por si acaso
                docker ps -a --filter "name=jenkins-zap-" --format '{{.ID}}' | xargs -r docker rm -f || true
                # Limpiar artefactos temporales
                rm -rf dependency-check dependency-check-9.2.0-release.zip || true
            '''
        }
        success {
            echo '✅ Pipeline completado correctamente.'
        }
        failure {
            echo '❌ Pipeline finalizó con errores.'
        }
    }
}
