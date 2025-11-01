// Este es el contenido de tu Jenkinsfile
pipeline {
    agent any // Le dice a Jenkins que puede usar cualquier "agente" o máquina disponible

    stages {
        stage('Build') { // Etapa 1: "Compilar" [cite: 69]
            steps {
                echo 'Building... (Para Python, es instalar dependencias)'
                // Aquí iría el build. Para este ejemplo, solo imprimimos un mensaje.
                // Si tuvieras un 'requirements.txt', aquí usarías:
                // sh 'pip install -r requirements.txt'
            }
        }

        stage('Test') { // Etapa 2: Pruebas Unitarias [cite: 70]
            steps {
                echo 'Running Unit Tests...'
                // Aquí correrías tus pruebas unitarias, si las tuvieras.
            }
        }

        stage('Analyze - SonarQube') { // Etapa 3: Análisis de Calidad [cite: 70]
            steps {
                echo 'Analyzing code with SonarQube...'
                // Este paso requiere la configuración del Paso 4
                // Debes tener el plugin "SonarQube Scanner" instalado
                // NOTA: Este es un ejemplo básico. Requiere configurar SonarQube en "Global Tool Configuration" de Jenkins.
                echo 'Omitiendo SonarQube por simplicidad de la guía, pero aquí se configuraría.'
                // El comando real sería algo como:
                // withSonarQubeEnv('MiSonarQubeServer') {
                //   sh '/ruta/a/sonar-scanner/bin/sonar-scanner'
                // }
            }
        }

        stage('Security Test (Static) - Dependency-Check') { // Etapa 4 (Parte 1): Seguridad Estática 
            steps {
                echo 'Checking for vulnerable dependencies...'
                // Este paso requiere el plugin del Paso 3
                // Necesita una configuración global en "Global Tool Configuration" -> "Dependency-Check"
                echo 'Omitiendo Dependency-Check por simplicidad, pero aquí se configuraría.'
                // El comando real sería:
                // dependencyCheck additionalArguments: '--scan . --format HTML', odcInstallation: 'NombreDeTuInstaladorDC'
            }
        }

        stage('Deploy (to Test Environment)') { // Etapa 5: Desplegar 
            steps {
                echo 'Deploying app to test environment...'
                // Para este ejercicio, "desplegar" será correr la app de Python
                // en segundo plano. La app se expone en el puerto 5000.
                sh 'nohup python app.py &'
                sleep 10 // Dar 10 segundos para que la app inicie
                echo 'App is running in the background.'
            }
        }

        stage('Security Test (Dynamic) - OWASP ZAP') { // Etapa 4 (Parte 2): Seguridad Dinámica 
            steps {
                echo 'Running dynamic scan with OWASP ZAP...'
                // Esto asume que ZAP está corriendo en localhost:8090 (Paso 5)
                // Y que la app está en localhost:5000 (Paso 6 - Deploy)
                // Este comando usa el script 'zap-baseline.py' que NO está en Jenkins por defecto.
                // Para simplificar, solo intentaremos conectarnos a ZAP.
                echo 'Omitiendo ZAP por simplicidad. Un comando real usaría un plugin de ZAP o un script.'
                // sh 'curl http://localhost:8090/' // Solo para probar conexión a ZAP
                // sh 'curl http://localhost:5000/hello?name=test' // Solo para probar conexión a la app
            }
        }
    }

    post { // Se ejecuta siempre al final
        always {
            echo 'Pipeline finished.'
            // Detener la aplicación de Python que dejamos corriendo
            sh 'pkill -f "python app.py" || true'
            echo 'Cleanup complete.'
        }
    }
}
