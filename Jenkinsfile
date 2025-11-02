pipeline {
    // 1. CONFIGURACIÓN DEL AGENTE
    // Usamos 'any' sin configuración especial dentro
    agent any
    
    // 2. CONFIGURACIÓN DE HERRAMIENTAS
    // Aquí declaramos las herramientas que Jenkins debe preparar
    tools {
        jdk 'jenkins-java'  // El JDK que configuraste en Global Tool Configuration
    }
    
    stages {
        // 3. ETAPA DE CONSTRUCCIÓN
        // Instala Python y las dependencias del proyecto
        stage('Build') {
            steps {
                echo 'Actualizando e instalando Python...'
                sh '''
                    apt-get update -qq
                    apt-get install -y python3 python3-pip
                '''
                
                echo 'Instalando dependencias de Python...'
                sh 'pip3 install --break-system-packages -r requirements.txt'
            }
        }

        // 4. ETAPA DE PRUEBAS (SIMULADA)
        stage('Test') {
            steps {
                echo 'Running Unit Tests... (Omitido por ahora)'
                // Aquí irían tus comandos de 'pytest', etc.
                // sh 'pytest tests/'
            }
        }

        // 5. ETAPA DE ANÁLISIS ESTÁTICO (SAST)
        // Analiza tu código con SonarQube
        stage('Analyze - SonarQube (SAST)') {
            steps {
                script {
                    // Obtenemos la ruta del SonarScanner configurado
                    def scannerHome = tool 'SonarScanner-Default' 
                    
                    // Usamos la configuración de SonarQube de la UI
                    withSonarQubeEnv('MiSonarQubeServer') { 
                        sh """
                            ${scannerHome}/bin/sonar-scanner \
                            -Dsonar.projectName=Proyecto-Python-Vulnerable \
                            -Dsonar.projectKey=py-vulnerable \
                            -Dsonar.sources=. \
                            -Dsonar.python.version=3
                        """
                    }
                }
            }
        }

        // 6. ETAPA DE QUALITY GATE (OPCIONAL - COMENTADA)
        // Descomenta si SonarQube tiene suficiente RAM
        /*
        stage('Check SonarQube Quality Gate') {
            steps {
                echo 'Revisando Quality Gate de SonarQube...'
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }
        */

        // 7. ETAPA DE ANÁLISIS DE DEPENDENCIAS (SCA)
        // Analiza vulnerabilidades en librerías con Dependency-Check
        stage('Security Test - Dependency-Check (SCA)') {
            steps {
                echo 'Analizando dependencias vulnerables...'
                
                // Usamos Dependency-Check instalado en Jenkins
                dependencyCheck(
                    additionalArguments: '''
                        --scan . 
                        --format HTML 
                        --format JSON
                        --project "Proyecto-Python-Vulnerable"
                        --enableExperimental
                        --out dependency-check-report
                    ''', 
                    odcInstallation: 'dependency-check'
                )
            }
            post {
                always {
                    // Publicamos los resultados
                    dependencyCheckPublisher pattern: 'dependency-check-report/dependency-check-report.xml'
                    
                    // Archivamos los reportes
                    archiveArtifacts artifacts: 'dependency-check-report/*', allowEmptyArchive: true
                }
            }
        }

        // 8. ETAPA DE DESPLIEGUE (A ENTORNO DE PRUEBAS)
        // Lanza la aplicación Flask en segundo plano
        stage('Deploy (to Test Environment)') {
            steps {
                echo 'Desplegando aplicación en entorno de pruebas...'
                
                script {
                    // Matamos cualquier proceso anterior de Python
                    sh 'pkill -f "python3 app.py" || true'
                    
                    // Iniciamos la app en segundo plano
                    sh 'nohup python3 app.py > app.log 2>&1 &'
                    
                    // Esperamos a que la app inicie
                    sleep 20
                    
                    // Verificamos que la app esté corriendo
                    sh '''
                        if curl -s http://localhost:5000/hello?name=test > /dev/null; then
                            echo "✓ App está corriendo correctamente"
                        else
                            echo "✗ Error: App no responde"
                            exit 1
                        fi
                    '''
                }
            }
        }

        // 9. ETAPA DE ANÁLISIS DINÁMICO (DAST)
        // Escanea la aplicación en ejecución con OWASP ZAP
        stage('Security Test - OWASP ZAP (DAST)') {
            steps {
                echo 'Ejecutando escaneo dinámico con OWASP ZAP...'
                
                script {
                    // Usamos el contenedor de ZAP que ya está corriendo
                    // Nota: Asegúrate de que el contenedor 'zap' esté en la misma red que Jenkins
                    
                    sh '''
                        # Instalamos Python3 si no está (para el script de ZAP)
                        which python3 || apt-get install -y python3
                        
                        # Descargamos el script baseline de ZAP
                        curl -s -o zap-baseline.py https://raw.githubusercontent.com/zaproxy/zaproxy/main/docker/zap-baseline.py
                        chmod +x zap-baseline.py
                        
                        # Ejecutamos el escaneo
                        # -t: URL objetivo (desde el contenedor Jenkins)
                        # -r: Genera reporte HTML
                        # -J: Genera reporte JSON
                        python3 zap-baseline.py \
                            -t http://localhost:5000 \
                            -r zap-baseline-report.html \
                            -J zap-baseline-report.json \
                            || true
                    '''
                    
                    echo '✓ Escaneo ZAP completado'
                }
            }
            post {
                always {
                    // Archivamos los reportes de ZAP
                    archiveArtifacts artifacts: 'zap-baseline-report.*', allowEmptyArchive: true
                }
            }
        }
    } // Fin de stages

    // 10. POST-ACTIONS
    // Acciones que se ejecutan al finalizar el pipeline
    post { 
        always {
            echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
            echo 'Pipeline finalizado. Limpiando recursos...'
            echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
            
            // Detenemos la aplicación Flask
            sh 'pkill -f "python3 app.py" || true'
            
            echo '✓ Limpieza completada'
        }
        
        success {
            echo '✓✓✓ PIPELINE EXITOSO ✓✓✓'
        }
        
        failure {
            echo '✗✗✗ PIPELINE FALLÓ ✗✗✗'
            echo 'Revisa los logs para más detalles'
        }
    }
}
