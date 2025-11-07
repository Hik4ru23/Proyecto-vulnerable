pipeline {
    // 1. CONFIGURACIÓN DEL AGENTE
    agent {
        any {
            tools {
                jdk 'jenkins-java'
            }
        }
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

        // 3. ETAPA DE ANÁLISIS ESTÁTICO (SAST)
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

        // 4. ETAPA DE ANÁLISIS DE DEPENDENCIAS (SCA)
        stage('Security Test (Static) - Dependency-Check (SCA)') {
            steps {
                echo 'Descargando y ejecutando Dependency-Check 9.2.0...'
                sh '''
                    # Descarga y extrae la última versión
                    wget -q https://github.com/jeremylong/DependencyCheck/releases/download/v9.2.0/dependency-check-9.2.0-release.zip
                    unzip -o dependency-check-9.2.0-release.zip

                    # Ejecuta el escaneo con actualización automática (solo la primera vez)
                    ./dependency-check/bin/dependency-check.sh \
                        --scan . \
                        --format HTML \
                        --project "Proyecto-Python-Vulnerable" \
                        --out dependency-check-report \
                        --data /var/jenkins_home/dependency-check-data \
                        --enableExperimental
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'dependency-check-report/**', fingerprint: true
                }
            }
        }

        // 5. ETAPA DE DESPLIEGUE (A PRUEBAS)
        stage('Deploy (to Test Environment)') {
            steps {
                echo 'Deploying app to test environment...'
                sh 'nohup python3 vulnerable.py &'
                sleep 15
                echo 'App is running in the background.'
            }
        }

        // 6. ETAPA DE ANÁLISIS DINÁMICO (DAST)
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

    // 7. ETAPA DE LIMPIEZA
    post {
        always {
            echo 'Pipeline finished. Cleaning up...'
            sh 'pkill -f "python3 vulnerable.py" || true'
            echo 'Cleanup complete.'
        }
    }
}
