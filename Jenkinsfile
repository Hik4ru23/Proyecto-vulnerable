pipeline {
    agent any

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
                sh '''
                    set -e
                    echo "➡️ Descargando Dependency-Check..."
                    wget -q https://github.com/jeremylong/DependencyCheck/releases/download/v9.2.0/dependency-check-9.2.0-release.zip
                    unzip -q dependency-check-9.2.0-release.zip
                    chmod +x dependency-check-9.2.0/bin/dependency-check.sh

                    echo "➡️ Ejecutando análisis..."
                    ./dependency-check-9.2.0/bin/dependency-check.sh \
                        --project "Proyecto Vulnerable" \
                        --scan . \
                        --format HTML \
                        --out dependency-check-report.html

                    echo "✅ Análisis completado correctamente."
                '''
            }
            post {
                success {
                    publishHTML([
                        reportDir: '.', 
                        reportFiles: 'dependency-check-report.html', 
                        reportName: 'Dependency Check Report'
                    ])
                }
                failure {
                    echo '❌ Dependency-Check falló.'
                }
            }
        }
    }

    post {
        always {
            echo '🧹 Limpiando entorno...'
            sh 'rm -rf dependency-check-9.2.0 dependency-check-9.2.0-release.zip || true'
        }
    }
}
