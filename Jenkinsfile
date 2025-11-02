pipeline {
    // ¡SIN BLOQUE 'tools' AQUÍ! Empezamos directo.
    agent any

    stages {
        stage('Build') {
            steps {
                echo 'Instalando dependencias de Python...'
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Test') {
            steps {
                echo 'Running Unit Tests... (Omitido por ahora)'
            }
        }

        stage('Analyze - SonarQube (SAST)') {
            steps {
                // Tuvimos que agregar 'script' para poder
                // obtener la ruta del scanner.
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

        stage('Check SonarQube Quality Gate') {
            steps {
                echo 'Revisando si el Quality Gate de SonarQube pasó...'
                timeout(time: 1, unit: 'HOURS') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Security Test (Static) - Dependency-Check (SCA)') {
            steps {
                echo 'Checking for vulnerable dependencies...'
                // Este paso no necesita el bloque 'tools' porque
                // 'odcInstallation' ya busca la herramienta 'DC-Default'
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
                sh 'nohup python app.py &'
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
            sh 'pkill -f "python app.py" || true'
            echo 'Cleanup complete.'
        }
    }
}
