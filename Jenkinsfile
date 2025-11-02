pipeline {
    // ¡CAMBIO! Le decimos al agente que prepare la herramienta JDK
    // que configuramos en la interfaz de Jenkins.
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
                sh 'apt-get install -y python3 python3-pip'
                
                echo 'Instalando dependencias de Python...'
                // Añadimos --break-system-packages para forzar la instalación
                sh 'pip3 install --break-system-packages -r requirements.txt'
            }
        }

        stage('Test') {
            steps {
                echo 'Running Unit Tests... (Omitido por ahora)'
            }
        }

        stage('Analyze - SonarQube (SAST)') {
            steps {
                script {
                    // 1. Pedirle a Jenkins la ruta del scanner 'SonarScanner-Default'
                    def scannerHome = tool 'SonarScanner-Default' 
                    
                    // 2. Usar la configuración del servidor y ejecutar el scanner
                    withSonarQubeEnv('MiSonarQubeServer') { 
                        // 3. Usamos la ruta completa al scanner
                        sh "${scannerHome}/bin/sonar-scanner \
                            -Dsonar.projectName=Proyecto-Python-Vulnerable \
                            -Dsonar.projectKey=py-vulnerable \
                            -Dsonar.sources=."
                    }
                }
            }
        }

        // --- ETAPA PROBLEMÁTICA COMENTADA ---
        // Esta etapa se saltará para evitar el atasco de 'PENDING'
        // stage('Check SonarQube Quality Gate') {
        //     steps {
        //         echo 'Revisando si el Quality Gate de SonarQube pasó...'
        //         timeout(time: 1, unit: 'HOURS') {
        //             waitForQualityGate abortPipeline: true
        //         }
        //     }
        // }
        // --- FIN DE LA ETAPA COMENTADA ---

        stage('Security Test (Static) - Dependency-Check (SCA)') {
            steps {
                echo 'Checking for vulnerable dependencies...'
                // Este comando usará el JDK 'jenkins-java' que definimos arriba
                dependencyCheck additionalArguments: '''
                    --scan . 
                    --format "HTML" 
                    --project "Proyecto-Python-Vulnerable"
                    --enableExperimental
                ''', odcInstallation: 'DC-Default'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'dependency-check-report.html'
                }
            }
        }

        stage('Deploy (to Test Environment)') {
            steps {
                echo 'Deploying app to test environment...'
                sh 'nohup python3 app.py &'
                sleep 15 
                echo 'App is running in the background.'
            }
        }

        stage('Security Test (Dynamic) - OWASP ZAP (DAST)') {
            steps {
                echo 'Running dynamic scan with OWASP ZAP...'
                
                sh 'curl -O https://raw.githubusercontent/zaproxy/zaproxy/main/docker/zap-baseline.py'
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
            sh 'pkill -f "python3 app.py" || true'
            echo 'Cleanup complete.'
        }
    }
}
