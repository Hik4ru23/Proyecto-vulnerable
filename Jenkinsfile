pipeline {
    agent any

    environment {
        SONARQUBE_ENV = credentials('sonar-token')
        NVD_API_KEY = credentials('NVD_API_KEY')
    }

    stages {

        stage('Build') {
            steps {
                echo 'Actualizando e instalando Python...'
                sh '''
                    apt-get update
                    apt-get install -y python3 python3-pip
                '''
                echo 'Instalando dependencias de Python...'
                sh 'pip3 install --break-system-packages -r requirements.txt'
            }
        }

        stage('Analyze - SonarQube (SAST)') {
            steps {
                script {
                    def scannerHome = tool 'SonarScanner-Default'
                    withSonarQubeEnv('MiSonarQubeServer') {
                        sh """
                            ${scannerHome}/bin/sonar-scanner \
                            -Dsonar.projectKey=py-vulnerable \
                            -Dsonar.projectName=Proyecto-Python-Vulnerable \
                            -Dsonar.sources=. \
                            -Dsonar.python.version=3.10
                        """
                    }
                }
            }
        }

        stage('Security Test (Static) - Dependency-Check (SCA)') {
            environment {
                NVD_API_KEY = credentials('NVD_API_KEY')
            }
            steps {
                echo 'Descargando y ejecutando Dependency-Check 9.2.0...'
                sh '''
                    wget -q https://github.com/jeremylong/DependencyCheck/releases/download/v9.2.0/dependency-check-9.2.0-release.zip
                    unzip -o dependency-check-9.2.0-release.zip

                    ./dependency-check/bin/dependency-check.sh \
                        --scan . \
                        --format HTML \
                        --project "Proyecto-Python-Vulnerable" \
                        --out dependency-check-report \
                        --data /var/jenkins_home/dependency-check-data \
                        --nvdApiKey "$NVD_API_KEY" \
                        --nvdApiDelay 8000 \
                        --enableExperimental || true
                '''
            }
            post {
                always {
                    echo 'Archivando reporte de Dependency-Check...'
                    archiveArtifacts artifacts: 'dependency-check-report/**', fingerprint: true
                }
            }
        }

        stage('Deploy (to Test Environment)') {
            when {
                expression { currentBuild.currentResult == 'SUCCESS' }
            }
            steps {
                echo 'Desplegando la aplicación en entorno de pruebas...'
                sh '''
                    nohup python3 vulnerable.py &
                    sleep 5
                '''
            }
        }

        stage('Security Test (Dynamic) - OWASP ZAP (DAST)') {
            when {
                expression { currentBuild.currentResult == 'SUCCESS' }
            }
            steps {
                echo 'Ejecutando OWASP ZAP...'
                sh '''
                    docker run --rm -v $(pwd):/zap/wrk/:rw \
                        ghcr.io/zaproxy/zaproxy:stable zap-baseline.py \
                        -t http://localhost:5000 \
                        -r zap-report.html || true
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'zap-report.html', fingerprint: true
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline finalizado. Limpiando entorno...'
            sh '''
                pkill -f python3 vulnerable.py || true
            '''
            echo 'Limpieza completa ✅'
        }
    }
}
