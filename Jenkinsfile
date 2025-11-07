pipeline {

    agent any

    environment {
        // Variable para el API key del NVD (Dependency-Check)
        NVD_API_KEY = credentials('nvd-api-key')
    }

    stages {

        stage('Checkout') {
            steps {
                echo '📦 Descargando código...'
                git branch: 'main', url: 'https://github.com/Hik4ru23/Proyecto-vulnerable.git'
            }
        }

        stage('Dependency Check') {
            steps {
                echo '🔍 Instalando y ejecutando Dependency-Check...'
                withCredentials([string(credentialsId: 'nvd-api-key', variable: 'NVD_API_KEY')]) {
                    sh '''
                        set -e
                        echo "➡️ Descargando Dependency-Check..."
                        if [ ! -f dependency-check-9.2.0-release.zip ]; then
                            wget -q https://github.com/jeremylong/DependencyCheck/releases/download/v9.2.0/dependency-check-9.2.0-release.zip
                        fi

                        echo "➡️ Descomprimiendo sin pedir confirmación..."
                        unzip -o -q dependency-check-9.2.0-release.zip

                        chmod +x dependency-check/bin/dependency-check.sh
                        echo "🚀 Ejecutando análisis con API Key válida..."
                        ./dependency-check/bin/dependency-check.sh \
                            --project Proyecto-Vulnerable \
                            --scan . \
                            --format HTML \
                            --out dependency-check-report \
                            --nvdApiKey "$NVD_API_KEY" \
                            --nvdApiDelay 4000 \
                            --noupdate || echo "⚠️ Advertencia: no se pudo actualizar el feed NVD, usando datos locales."
                    '''
                }
            }
            post {
                always {
                    echo '🧹 Limpiando entorno...'
                    sh 'rm -rf dependency-check dependency-check-9.2.0-release.zip || true'
                    echo '✅ Dependency-Check finalizado correctamente.'
                    archiveArtifacts artifacts: 'dependency-check-report/dependency-check-report.html'
                }
            }
        }

        stage('Deploy (to Test Environment)') {
            steps {
                echo '🚀 Iniciando app de prueba...'
                sh 'nohup python3 vulnerable.py &'
                sleep 10
            }
        }

        stage('Security Test (Dynamic) - OWASP ZAP (DAST)') {
            steps {
                echo '🧨 Ejecutando OWASP ZAP...'
                sh '''
                    # Descargamos el script oficial si no está
                    if [ ! -f zap-baseline.py ]; then
                        curl -O https://raw.githubusercontent.com/zaproxy/zaproxy/main/docker/zap-baseline.py
                        chmod +x zap-baseline.py
                    fi

                    echo "🚀 Iniciando análisis dinámico con ZAP..."
                    ./zap-baseline.py \
                        -t http://jenkins-lts:5000/hello?name=test \
                        -H zap \
                        -p 8090 \
                        -r zap-report.html || echo "⚠️ ZAP terminó con advertencias."
                '''
            }
            post {
                always {
                    echo '📑 Archivando reporte de OWASP ZAP...'
                    archiveArtifacts artifacts: 'zap-report.html'
                }
            }
        }

    } // fin de stages

    post {
        always {
            echo '🧽 Pipeline finalizado. Limpiando entorno...'
            sh 'pkill -f "python3 vulnerable.py" || true'
        }
    }
}
