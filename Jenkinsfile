pipeline {
    // 1. CONFIGURACIÓN DEL AGENTE
    // Le decimos a Jenkins que prepare la herramienta JDK 'jenkins-java'
    // que configuramos en "Global Tool Configuration".
    // Esto arregla el error "Couldn’t find any executable in 'null'".
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
                // La imagen jenkins:lts no trae Python. Lo instalamos como 'root'.
                sh 'apt-get update'
                sh 'apt-get install -y python3 python3-pip'
                
                echo 'Instalando dependencias de Python...'
                // Usamos --break-system-packages para evitar el error de "externally-managed-environment".
                sh 'pip3 install --break-system-packages -r requirements.txt'
            }
        }

        // 3. ETAPA DE PRUEBAS (SIMULADA)
        stage('Test') {
            steps {
                echo 'Running Unit Tests... (Omitido por ahora)'
                // Aquí irían tus comandos de 'pytest', etc.
            }
        }

        // 4. ETAPA DE ANÁLISIS ESTÁTICO (SAST)
        // Analiza tu propio código (app.py) con SonarQube.
        stage('Analyze - SonarQube (SAST)') {
            steps {
                script {
                    // Obtenemos la ruta del 'SonarScanner-Default' que configuramos en la UI
                    def scannerHome = tool 'SonarScanner-Default' 
                    
                    // Usamos la configuración 'MiSonarQubeServer' de la UI
                    withSonarQubeEnv('MiSonarQubeServer') { 
                        sh "${scannerHome}/bin/sonar-scanner \
                            -Dsonar.projectName=Proyecto-Python-Vulnerable \
                            -Dsonar.projectKey=py-vulnerable \
                            -Dsonar.sources=."
                    }
                }
            }
        }

        // 5. ETAPA DE QUALITY GATE (DESACTIVADA)
        // Esta etapa la comentamos para evitar los atascos ('PENDING' / 'IN_PROGRESS')
        // causados por la falta de RAM en SonarQube.
        // En un entorno real, la activarías.
        // stage('Check SonarQube Quality Gate') {
        //     steps {
        //         echo 'Revisando si el Quality Gate de SonarQube pasó...'
        //         timeout(time: 1, unit: 'HOURS') {
        //             waitForQualityGate abortPipeline: true
        //         }
        //     }
        // }
        // --- FIN DE LA ETAPA COMENTADA ---

        // 6. ETAPA DE ANÁLISIS DE DEPENDENCIAS (SCA)
        // Analiza tus librerías (Flask) con Dependency-Check.
        stage('Security Test (Static) - Dependency-Check (SCA)') {
            steps {
                echo 'Checking for vulnerable dependencies...'
                // Usará el JDK 'jenkins-java' y la herramienta 'DC-Default'
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

        // 7. ETAPA DE DESPLIEGUE (A PRUEBAS)
        // Lanza tu aplicación app.py en segundo plano.
        stage('Deploy (to Test Environment)') {
            steps {
                echo 'Deploying app to test environment...'
                // Usamos 'nohup' para que corra en segundo plano
                // y 'python3' porque es el que instalamos.
                sh 'nohup python3 app.py &'
                sleep 15 // Dar 15 segundos para que la app inicie
                echo 'App is running in the background.'
            }
        }

        // 8. ETAPA DE ANÁLISIS DINÁMICO (DAST)
        // Ataca tu aplicación (que ya está corriendo) con OWASP ZAP.
        stage('Security Test (Dynamic) - OWASP ZAP (DAST)') {
            steps {
                echo 'Running dynamic scan with OWASP ZAP...'
                
                // Descargamos el script de ZAP
                sh 'curl -O https://raw.githubusercontent/zaproxy/zaproxy/main/docker/zap-baseline.py'
                sh 'chmod +x zap-baseline.py'
                
                // Ejecutamos el escaneo
                sh '''
                    ./zap-baseline.py \
                    -t http://jenkins-lts:5000/hello?name=test \
                    -H zap \
                    -p 8090 \
                    -J zap-baseline-report.json
                '''
                // -t http://jenkins-lts:5000 -> Ataca la app (en el contenedor 'jenkins-lts')
                // -H zap -> Le habla a la API de ZAP (en el contenedor 'zap')
            }
            post {
                always {
                    // Guarda el reporte JSON
                    archiveArtifacts artifacts: 'zap-baseline-report.json'
                }
            }
        }
    } // Fin de 'stages'

    // 9. ETAPA DE LIMPIEZA
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
