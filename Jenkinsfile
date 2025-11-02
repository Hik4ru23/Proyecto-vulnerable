pipeline {
    // 1. CONFIGURACIÓN DEL AGENTE
    agent {
        any {
            tools {
                jdk 'jenkins-java'
            }
        }
    }

    environment {
        JAVA_HOME = '/opt/java/openjdk'
    }
    
    stages {
        // 2. ETAPA DE CONSTRUCCIÓN
        stage('Build') {
            steps {
                echo 'Actualizando e instalando Python...'
                sh 'apt-get update'
                sh 'apt-get install -y python3 python3-pip'
                
                echo 'Instalando dependencias de Python...'
                sh 'pip3 install --break-system-packages -r requirements.txt'
            }
        }

        // 3. ETAPA DE PRUEBAS (SIMULADA)
        stage('Test') {
            steps {
                echo 'Running Unit Tests... (Omitido por ahora)'
            }
        }

        // 4. ANÁLISIS ESTÁTICO (SAST)
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

        // 5. QUALITY GATE (Desactivada)
        // stage('Check SonarQube Quality Gate') { ... }

        // 6. ANÁLISIS DE DEPENDENCIAS (SCA)
        stage('Security Test (Static) - Dependency-Check (SCA)') {
            steps {
                echo 'Checking for vulnerable dependencies...'
                script {
                    // Ejecutamos Dependency-Check pero evitamos que el pipeline falle si hay vulnerabilidades
                    def status = sh(
                        script: '''
                            /opt/dependency-check/dependency-check/bin/dependency-check.sh \
                                --project "Proyecto-Python-Vulnerable" \
                                --scan . \
                                --format "HTML" \
                                --out dependency-check-report \
                                --enableExperimental \
                                || true
                        ''',
                        returnStatus: true
                    )

                    echo "Dependency-Check exit code: ${status}"
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'dependency-check-report/dependency-check-report.html', fingerprint: true
                }
            }
        }

        // 7. DESPLIEGUE (A PRUEBAS)
        stage('Deploy (to Test Environment)') {
            steps {
                echo 'Deploying app to test environment...'
                sh 'nohup python3 app.py &'
                sleep 15
                echo 'App is running in the background.'
            }
        }

        // 8. ANÁLISIS DINÁMICO (DAST)
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
                    archiveArtifacts artifacts: 'zap-baseline-report.json', fingerprint: true
                }
            }
        }
    }

    // 9. LIMPIEZA FINAL
    post { 
        always {
            echo 'Pipeline finished. Cleaning up...'
            sh 'pkill -f "python3 app.py" || true'
            echo 'Cleanup complete.'
        }
    }
}
