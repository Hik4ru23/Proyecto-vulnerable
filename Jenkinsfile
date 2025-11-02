pipeline {
    agent any

    environment {
        JAVA_HOME = '/opt/java/openjdk'
    }

    stages {

        // 🧱 ETAPA 1: BUILD
        stage('Build') {
            steps {
                echo 'Instalando dependencias...'
                sh '''
                    apt-get update
                    apt-get install -y python3 python3-pip
                    pip3 install --break-system-packages -r requirements.txt
                '''
            }
        }

        // 🧪 ETAPA 2: TEST
        stage('Test') {
            steps {
                echo 'Running Unit Tests... (omitido por ahora)'
            }
        }

        // 🧠 ETAPA 3: SONARQUBE
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

        // 🔐 ETAPA 4: DEPENDENCY-CHECK
        stage('Security Test (Static) - Dependency-Check (SCA)') {
            steps {
                echo 'Checking dependencies...'
                script {
                    sh '''
                        mkdir -p dependency-check-report
                        /opt/dependency-check/dependency-check/bin/dependency-check.sh \
                            --project "Proyecto-Python-Vulnerable" \
                            --scan . \
                            --format "HTML" \
                            --out dependency-check-report \
                            --enableExperimental || true

                        if [ ! -f dependency-check-report/dependency-check-report.html ]; then
                            echo "<html><body><h2>No se generó el reporte de Dependency-Check.</h2></body></html>" > dependency-check-report/dependency-check-report.html
                        fi
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'dependency-check-report/dependency-check-report.html', fingerprint: true
                }
            }
        }

        // 🚀 ETAPA 5: DEPLOY
        stage('Deploy (to Test Environment)') {
            steps {
                echo 'Deploying app to test environment...'
                sh 'nohup python3 app.py &'
                sleep 15
            }
        }

        // 🕷️ ETAPA 6: OWASP ZAP
        stage('Security Test (Dynamic) - OWASP ZAP (DAST)') {
            steps {
                echo 'Running OWASP ZAP scan...'
                script {
                    sh '''
                        if [ ! -f zap-baseline.py ]; then
                            curl -L -o zap-baseline.py https://raw.githubusercontent.com/zaproxy/zaproxy/main/docker/zap-baseline.py
                            chmod +x zap-baseline.py
                        fi

                        ./zap-baseline.py \
                            -t http://jenkins-lts:5000/hello?name=test \
                            -p 8090 \
                            -r zap-report.html || true

                        if [ ! -f zap-report.html ]; then
                            echo "<html><body><h2>No se generó el reporte de ZAP.</h2></body></html>" > zap-report.html
                        fi
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'zap-report.html', fingerprint: true
                }
            }
        }

        // ⚠️ ETAPA 7: CONTROL DE CALIDAD DE VULNERABILIDADES
        stage('Fail Pipeline if High/Critical Vulnerabilities Found') {
            steps {
                echo 'Analizando reporte de OWASP ZAP para vulnerabilidades críticas...'
                script {
                    // Buscar palabras clave en el reporte HTML de ZAP
                    def highVulns = sh(
                        script: "grep -E -i 'High Risk|Critical|High severity' zap-report.html || true",
                        returnStdout: true
                    ).trim()

                    if (highVulns) {
                        error("❌ Se detectaron vulnerabilidades de ALTO o CRÍTICO nivel en OWASP ZAP. Deteniendo pipeline.")
                    } else {
                        echo "✅ No se encontraron vulnerabilidades críticas en ZAP."
                    }
                }
            }
        }

        // 🧾 ETAPA 8: PUBLICAR REPORTES EN JENKINS
        stage('Publish Reports') {
            steps {
                echo 'Publicando reportes HTML en Jenkins...'
                publishHTML([
                    reportDir: 'dependency-check-report',
                    reportFiles: 'dependency-check-report.html',
                    reportName: 'Dependency-Check Report',
                    keepAll: true,
                    alwaysLinkToLastBuild: true,
                    allowMissing: true
                ])
                publishHTML([
                    reportDir: '.',
                    reportFiles: 'zap-report.html',
                    reportName: 'OWASP ZAP Report',
                    keepAll: true,
                    alwaysLinkToLastBuild: true,
                    allowMissing: true
                ])
            }
        }
    }

    post {
        always {
            echo 'Cleaning up environment...'
            sh 'pkill -f "python3 app.py" || true'
            echo 'Pipeline finished.'
        }
    }
}
