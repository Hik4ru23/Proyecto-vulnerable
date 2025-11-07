pipeline {
    agent any

    environment {
        DEP_CHECK_VERSION = "9.2.0"
    }

    stages {
        stage('Checkout') {
            steps {
                echo "📦 Descargando código..."
                git branch: 'main', url: 'https://github.com/Hik4ru23/Proyecto-vulnerable.git'
            }
        }

        stage('Dependency Check') {
            steps {
                echo "🔍 Instalando y ejecutando Dependency-Check..."
                withCredentials([string(credentialsId: 'NVD_API_KEY', variable: 'NVD_API_KEY')]) {
                    sh '''
                        set -e

                        echo "➡️ Descargando Dependency-Check..."
                        if [ ! -f dependency-check-${DEP_CHECK_VERSION}-release.zip ]; then
                            wget -q https://github.com/jeremylong/DependencyCheck/releases/download/v${DEP_CHECK_VERSION}/dependency-check-${DEP_CHECK_VERSION}-release.zip
                        fi

                        echo "➡️ Descomprimiendo sin pedir confirmación..."
                        unzip -o -q dependency-check-${DEP_CHECK_VERSION}-release.zip

                        chmod +x dependency-check/bin/dependency-check.sh

                        echo "🚀 Ejecutando análisis con API Key y delay..."
                        ./dependency-check/bin/dependency-check.sh \
                            --project "Proyecto-Vulnerable" \
                            --scan . \
                            --format "HTML" \
                            --out dependency-check-report.html \
                            --nvdApiKey "$NVD_API_KEY" \
                            --nvdApiDelay 2000
                    '''
                }
            }
            post {
                success {
                    echo "✅ Dependency-Check completado exitosamente."
                    archiveArtifacts artifacts: 'dependency-check-report.html', fingerprint: true
                }
                failure {
                    echo "❌ Dependency-Check falló."
                }
            }
        }
    }

    post {
        always {
            echo "🧹 Limpiando entorno..."
            sh 'rm -rf dependency-check dependency-check-*.zip'
        }
    }
}
