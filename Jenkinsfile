pipeline {
    agent any

    environment {
        NVD_API_KEY = credentials('NVD_API_KEY') // Nombre del secreto en Jenkins Credentials
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
                withCredentials([string(credentialsId: 'NVD_API_KEY', variable: 'NVD_API_KEY')]) {
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
                            --nvdApiDelay 4000 \
                            --noupdate || echo "⚠️ Advertencia: no se pudo actualizar el feed NVD, usando datos locales."
                    '''
                }
            }
            post {
                success {
                    echo '✅ Dependency-Check finalizado correctamente.'
                    archiveArtifacts artifacts: 'dependency-check-report.html', allowEmptyArchive: true
                }
                failure {
                    echo '❌ Dependency-Check falló.'
                }
                always {
                    echo '🧹 Limpiando entorno...'
                    sh 'rm -rf dependency-check dependency-check-9.2.0-release.zip'
                }
            }
        }
    }
}
