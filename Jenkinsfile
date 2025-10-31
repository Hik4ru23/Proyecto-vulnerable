pipeline {
    agent any

    environment {
        // Configura aquí tu servidor SonarQube si lo usas
        SONARQUBE_SERVER = 'MySonarQube'    // Nombre configurado en Jenkins
        SONAR_PROJECT_KEY = 'mi-proyecto'   // Clave única de tu proyecto en SonarQube
    }

    stages {
        /* -------------------------- ETAPA 1: BUILD -------------------------- */
        stage('Build') {
            steps {
                echo '🔧 Compilando y preparando el proyecto...'
                // Ejemplo: si tu proyecto usa Python o Node
                // sh 'pip install -r requirements.txt'
                // o: sh 'npm install'
            }
        }

        /* --------------------------- ETAPA 2: TEST --------------------------- */
        stage('Test') {
            steps {
                echo '🧪 Ejecutando pruebas unitarias...'
                // Ejemplo de pruebas (ajusta según tu lenguaje)
                // sh 'pytest || echo "No hay pruebas unitarias definidas"'
            }
        }

        /* -------------------------- ETAPA 3: SONARQUBE ----------------------- */
        stage('Analyze - SonarQube') {
            steps {
                echo '📊 Analizando calidad de código con SonarQube...'
                withSonarQubeEnv("${SONARQUBE_SERVER}") {
                    // Asegúrate de tener configurado el Sonar Scanner en Jenkins
                    sh """
                    sonar-scanner \
                        -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                        -Dsonar.sources=. \
                        -Dsonar.language=py \
                        -Dsonar.sourceEncoding=UTF-8
                    """
                }
            }
        }

        /* --------------------- ETAPA 4: DEPENDENCY-CHECK --------------------- */
        stage('Security - Dependency Check') {
            steps {
                echo '🛡️ Ejecutando análisis de dependencias (OWASP Dependency-Check)...'
                // Analiza dependencias del proyecto y genera un reporte HTML
                dependencyCheck additionalArguments: '--scan . --format HTML --out reports', odcInstallation: 'Default'
                dependencyCheckPublisher pattern: 'reports/dependency-check-report.html'
            }
        }

        /* -------------------------- ETAPA 5: OWASP ZAP ----------------------- */
        stage('Security - OWASP ZAP') {
            steps {
                echo '🔍 Ejecutando escaneo dinámico de seguridad (OWASP ZAP)...'
                // Ejecuta ZAP en Docker y genera reporte HTML
                sh '''
                docker run --rm -v $(pwd):/zap/wrk owasp/zap2docker-stable \
                zap-baseline.py -t http://localhost:5000 -r zap-report.html || true
                '''
                // Publica el reporte como artefacto del build
                archiveArtifacts artifacts: 'zap-report.html'
            }
        }

        /* --------------------------- ETAPA 6: DEPLOY ------------------------- */
        stage('Deploy') {
            steps {
                echo '🚀 Desplegando la aplicación en entorno de pruebas...'
                // Ejemplo simple (si usas Docker Compose)
                // sh 'docker-compose up -d'
            }
        }
    }

    /* -------------------------- ETAPA FINAL (POST) -------------------------- */
    post {
        always {
            echo '🧹 Limpieza final del pipeline...'
            sh 'docker system prune -f || true'
        }
        success {
            echo '✅ Pipeline ejecutado correctamente.'
        }
        failure {
            echo '❌ Falló alguna etapa del pipeline. Revisar logs.'
        }
    }
}
