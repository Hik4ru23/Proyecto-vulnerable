pipeline {
    // 1. CONFIGURACIÓN DEL AGENTE
    // Le decimos a Jenkins que prepare la herramienta JDK 'jenkins-java'
    // que configuraste en "Global Tool Configuration".
    agent {
        any {
            tools {
                jdk 'jenkins-java'
            }
        }
    }
    
    stages {
        // 2. ETAPA DE CONSTRUCCIÓN
        // Instala Python y las dependencias del proyecto.
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
        // Analiza tu propio código (app.py) con SonarQube.
        stage('Analyze - SonarQube (SAST)') {
            steps {
                script {
                    // Obtenemos la ruta del 'SonarScanner-Default' que configuramos en la UI
                    def scannerHome = tool 'SonarScanner-Default' 
                    
                    // Usamos la configuración 'MiSonarQubeServer' de la UI
                    withSonarQubeEnv('MiSonarQubeServer') { 
                        // Comando de SonarQube simplificado a una línea
                        sh "${scannerHome}/bin/sonar-scanner -Dsonar.projectName=Proyecto-Python-Vulnerable -Dsonar.projectKey=py-vulnerable -Dsonar.sources=."
                    }
                }
            }
        }

        // 4. ETAPA DE QUALITY GATE (DESACTIVADA)
        // La mantenemos comentada para evitar los atascos por falta de RAM
        // stage('Check SonarQube Quality Gate') {
        //     steps {
        //         echo 'Revisando si el Quality Gate de SonarQube pasó...'
        //         timeout(time: 1, unit: 'HOURS') {
        //             waitForQualityGate abortPipeline: true
        //         }
        //     }
        // }

        // 5. ETAPA DE ANÁLISIS DE DEPENDENCIAS (SCA)
        // Analiza tus librerías (Flask) con Dependency-Check.
        stage('Security Test (Static) - Dependency-Check (SCA)') {
            steps {
                echo 'Checking for vulnerable dependencies...'
                dependencyCheck additionalArguments: '''
                    --scan . 
                    --format "HTML" 
                    --project "Proyecto-Python-Vulnerable"
                    --enableExperimental
                ''', odcInstallation: 'DC-Default'
            }
            post {
                always {
                    // Guarda el reporte para verlo en la UI de Jenkins
                    archiveArtifacts artifacts: 'dependency-check-report.html'
                }
            }
        }

        // 6. ETAPA DE DESPLIEGUE (A PRUEBAS)
        // Lanza tu aplicación app.py en segundo plano.
        stage('Deploy (to Test Environment)') {
            steps {
                echo 'Deploying app to test environment...'
                sh 'nohup python3 app.py &'
                sleep 15 // Dar 15 segundos para que la app inicie
                echo 'App is running in the background.'
            }
        }

        // 7. ETAPA DE ANÁLISIS DINÁMICO (DAST)
        // Ataca tu aplicación (que ya está corriendo) con OWASP ZAP.
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
                    // Guarda el reporte JSON
                    archiveArtifacts artifacts: 'zap-baseline-report.json'
                }
            }
        }
    } // Fin de 'stages'

    // 8. ETAPA DE LIMPIEZA
    // Se ejecuta siempre, falle o no el pipeline.
    post { 
        always {
            echo 'Pipeline finished. Cleaning up...'
            // Detiene el servidor de Python
            sh 'pkill -f "python3 app.py" || true'
            echo 'Cleanup complete.'
        }
    }
}
