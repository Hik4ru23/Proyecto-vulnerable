pipeline {
    agent any

    environment {
        // Configura tu servidor SonarQube (mismo nombre que en "Manage Jenkins → Configure System")
        SONARQUBE_SERVER = 'MySonarQube'
        // Clave del proyecto configurada en SonarQube
        SONAR_PROJECT_KEY = 'mi-proyecto'
    }

    stages {

        /* -------------------------- ETAPA 1: BUILD -------------------------- */
        stage('Build') {
            steps {
                echo '🔧 Compilando y preparando el proyecto...'
                // Ejemplo: si tu proyecto usa Python o Node.js
                // sh 'pip install -r requirements.txt'
                // sh 'npm install'
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
                script {
                    // Inyecta variables del servidor SonarQube configurado
                    withSonarQubeEnv("${SONARQUBE_SERVER}") {
                        // Busca la herramienta Sonar Scanner configurada en Jenkins
                        def scannerHome = tool name: 'sonar-scanner', type: 'hudson.plugins.sonar.SonarRunnerInstallation'

                        // Ejecuta el análisis de calidad de código
                        sh """
                            ${scannerHome}/bin/sonar-scanner \
                                -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                                -Dsonar.sources=. \
                                -Dsonar.language=py \
                                -Dsonar.sourceEncoding=UTF-8
                        """
                    }
                }
            }
        }

        /* --------------------- ETAPA 4: DEPENDENCY-CHECK --------------------- */
        stage('Security - Dependency Check') {
            steps {
                echo '🛡️ Ejecutando análisis de dependencias (OWASP Dependency-Check)...'
                // Analiza dependencias y genera un reporte HTML
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
                    zap-baseline.py -t http://host.docker.internal:5000 -r zap-report.html || true
                '''
                // Publica el reporte como artefacto del build
                archiveArtifacts artifacts: 'zap-report.html'
            }
        }

        /* --------------------------- ETAPA 6: DEPLOY ------------------------- */
        stage('Deploy') {
            steps {
                echo '🚀 Desplegando la aplicación en entorno de pruebas...'
                // Ejemplo: levantar servicios con Docker Compose
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
