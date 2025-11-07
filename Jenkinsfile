pipeline {
    agent {
        any {
            tools {
                jdk 'jenkins-java'
            }
        }
    }

    stages {

        stage('Build') {
            steps {
                echo 'Actualizando e instalando Python...'
                sh 'apt-get update'
                sh 'apt-get install -y python3 python3-pip unzip wget'

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
                            -Dsonar.projectName=Proyecto-Python-Vulnerable \
                            -Dsonar.projectKey=py-vulnerable \
                            -Dsonar.sources=.
                        """
                    }
                }
            }
        }

        // 🔹 Actualización y ejecución manual de Dependency-Check 9.2.0
        stage('Security Test (Static) - Dependency-Check (SCA)') {
            steps {
                echo 'Descargando y ejecutando Dependency-Check 9.2.0...'

                sh '''
                    # Descargar y descomprimir la versión más reciente
                    wget -q https://github.com/jeremylong/DependencyCheck/releases/download/v9.2.0/dependency-check-9.2.0-release.zip -O dependency-check.zip
                    unzip -o dependency-check.zip

                    # Verificar versión
                    ./dependency-check/bin/dependency-check.sh --version

                    # Ejecutar análisis
                    ./dependency-check/bin/dependency-check.sh \
                        --scan . \
                        --format HTML \
                        --project "Proyecto-Python-Vulnerable" \
                        --out dependency-check-report \
                        --enableExperimental \
                        --noupdate
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'dependency-check-report/**', fingerprint: true
                }
            }
        }

        stage('Deploy (to Test Environment)') {
            steps {
                echo 'Deploying app to test environment...'
                sh 'nohup python3 vulnerable.py &'
                sleep 15
                echo 'App is running in the background.'
            }
        }

        stage('Security Test (Dynamic) - OWASP ZAP (DAST)') {
            steps {
                echo 'Running dynamic scan with OWASP ZAP...'

                sh 'curl -O https://raw.githubusercontent.com/zaproxy/zaproxy/main/docker/zap-baseline.py'
                sh 'chmod +x zap-baseline.py'

                sh '''
                    ./zap-baseline.py \
                    -t http://jenkins-lts:5000/hello?name=test \
                    -H zap \
                    -p 8090 \
                    -J zap-baseline-report.json
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'zap-baseline-report.json'
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished. Cleaning up...'
            sh 'pkill -f "python3 vulnerable.py" || true'
            echo 'Cleanup complete.'
        }
    }
}
