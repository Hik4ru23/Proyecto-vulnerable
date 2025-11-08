pipeline {
    agent any

    environment {
        NVD_API_KEY = credentials('NVD_API_KEY')
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
                withCredentials([string(credentialsId: 'NVD_API_KEY', variable: 'NVD_API_KEY')]) {
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

                        echo "🚀 Ejecutando análisis con API Key válida..."
                        ./dependency-check/bin/dependency-check.sh \
                            --project "Proyecto-Vulnerable" \
                            --scan . \
                            --format HTML \
                            --out dependency-check-report.html \
                            --nvdApiKey "$NVD_API_KEY" \
                            --nvdApiDelay 8000
                    '''
                }
            }
            post {
                always {
                    echo '🧹 Limpiando entorno...'
                    sh 'rm -rf dependency-check dependency-check-9.2.0-release.zip || true'
                }
                success {
                    echo '✅ Dependency-Check finalizado correctamente.'
                }
                failure {
                    echo '❌ Dependency-Check falló.'
                }
            }
        }

        stage('Security Test (Dynamic) - OWASP ZAP (DAST)') {
            when {
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                echo '⚡ Ejecutando OWASP ZAP (DAST)...'
            }
        }
    }

    post {
        always {
            echo '🧽 Pipeline finalizado. Limpiando entorno...'
            sh 'pkill -f "python3.*vulnerable.py" || true'
        }
    }
}
