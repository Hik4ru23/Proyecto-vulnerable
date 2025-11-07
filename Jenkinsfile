pipeline {
    agent any

    environment {
        SONARQUBE = credentials('sonar-token')
        DEP_CHECK_PATH = './dependency-check-9.2.0/bin/dependency-check.sh'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/Hik4ru23/Proyecto-vulnerable.git'
            }
        }

        stage('Dependency Check') {
            steps {
                echo '🔍 Ejecutando Dependency-Check...'
                sh '''
                    wget -q https://github.com/jeremylong/DependencyCheck/releases/download/v9.2.0/dependency-check-9.2.0-release.zip
                    unzip -q dependency-check-9.2.0-release.zip
                    ${DEP_CHECK_PATH} --project "Proyecto Vulnerable" --scan . --format HTML --out dependency-check-report.html
                '''
            }
            post {
                success {
                    echo '✅ Dependency-Check completado correctamente.'
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

        stage('SonarQube Analysis') {
            steps {
                echo '🔎 Analizando con SonarQube...'
                withSonarQubeEnv('SonarQube') {
                    sh '''
                        sonar-scanner \
                        -Dsonar.projectKey=ProyectoVulnerable \
                        -Dsonar.sources=. \
                        -Dsonar.host.url=http://localhost:9000 \
                        -Dsonar.login=${SONARQUBE}
                    '''
                }
            }
        }
    }

    post {
        always {
            script {
                echo '🧹 Pipeline finalizado. Limpiando entorno...'
                sh 'rm -rf dependency-check-9.2.0 dependency-check-9.2.0-release.zip'
            }
        }
    }
}
