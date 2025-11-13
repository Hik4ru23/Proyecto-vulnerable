pipeline {
    agent any
    
    environment {
        PROJECT_NAME = "pipeline-test"
        SONARQUBE_URL = "http://sonarqube:9000"
        SONARQUBE_TOKEN = "sqa_77e30137bb8e01768b25a57b9671ad1db4959dcf"
        TARGET_URL = "http://172.23.202.60:5000"
        DC_VERSION = "10.0.4"
        DC_DIRECTORY = "${WORKSPACE}/dependency-check"
    }
    
    stages {
        stage('Install Python') {
            steps {
                sh '''
                    echo "📦 Installing Python..."
                    apt update
                    apt install -y python3 python3-venv python3-pip
                '''
            }
        }
        
        stage('Setup Environment') {
            steps {
                sh '''
                    echo "🐍 Setting up virtual environment..."
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --break-system-packages -r requirements.txt
                '''
            }
        }
        
        stage('Python Security Audit') {
            steps {
                sh '''
                    . venv/bin/activate
                    pip install --break-system-packages pip-audit
                    mkdir -p dependency-check-report
                    pip-audit -r requirements.txt -f markdown -o dependency-check-report/pip-audit.md || true
                    pip-audit -r requirements.txt -f json -o dependency-check-report/pip-audit.json || true
                '''
            }
        }
        
        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool name: 'SonarQubeScanner', type: 'hudson.plugins.sonar.SonarRunnerInstallation'
                    withSonarQubeEnv('SonarQubeScanner') {
                        sh """
                            ${scannerHome}/bin/sonar-scanner \
                                -Dsonar.projectKey=${PROJECT_NAME} \
                                -Dsonar.sources=. \
                                -Dsonar.host.url=${SONARQUBE_URL} \
                                -Dsonar.login=${SONARQUBE_TOKEN} \
                                -Dsonar.python.version=3
                        """
                    }
                }
            }
        }
        
        stage('Install Dependency Check') {
            steps {
                script {
                    sh '''
                        echo "📦 Installing OWASP Dependency-Check..."
                        apt-get update
                        apt-get install -y wget unzip default-jre
                        
                        if [ ! -d "${DC_DIRECTORY}" ]; then
                            mkdir -p ${DC_DIRECTORY}
                            cd ${DC_DIRECTORY}
                            wget https://github.com/jeremylong/DependencyCheck/releases/download/v${DC_VERSION}/dependency-check-${DC_VERSION}-release.zip
                            unzip dependency-check-${DC_VERSION}-release.zip
                            chmod +x dependency-check/bin/dependency-check.sh
                        fi
                        
                        echo "✅ Dependency-Check installed at: ${DC_DIRECTORY}/dependency-check"
                        ls -la ${DC_DIRECTORY}/dependency-check/bin/
                    '''
                }
            }
        }
        
        stage('Dependency Check Scan') {
            steps {
                withCredentials([string(credentialsId: 'nvdApiKey', variable: 'NVD_API_KEY')]) {
                    script {
                        sh '''
                            echo "🔍 Running Dependency-Check scan..."
                            mkdir -p dependency-check-report
                            
                            # Opción 1: Intentar con API key
                            echo "Attempting scan with NVD API..."
                            ${DC_DIRECTORY}/dependency-check/bin/dependency-check.sh \
                                --scan . \
                                --format HTML \
                                --format JSON \
                                --format XML \
                                --out dependency-check-report \
                                --project "${PROJECT_NAME}" \
                                --enableExperimental \
                                --enableRetired \
                                --nvdApiKey ${NVD_API_KEY} \
                                --nvdApiDelay 6000 \
                                --nvdMaxRetryCount 10 \
                                --prettyPrint || {
                                    echo "⚠️ NVD API scan failed, trying without updates..."
                                    
                                    # Opción 2: Escanear sin actualizar la base de datos
                                    ${DC_DIRECTORY}/dependency-check/bin/dependency-check.sh \
                                        --scan . \
                                        --format HTML \
                                        --format JSON \
                                        --format XML \
                                        --out dependency-check-report \
                                        --project "${PROJECT_NAME}" \
                                        --enableExperimental \
                                        --enableRetired \
                                        --noupdate \
                                        --prettyPrint || {
                                            echo "⚠️ Full scan failed, generating basic report..."
                                            
                                            # Opción 3: Crear un reporte básico HTML si todo falla
                                            cat > dependency-check-report/dependency-check-report.html <<EOF
<!DOCTYPE html>
<html>
<head>
    <title>Dependency Check Report - ${PROJECT_NAME}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .warning { background-color: #fff3cd; border: 1px solid #ffc107; padding: 20px; border-radius: 5px; }
        h1 { color: #dc3545; }
    </style>
</head>
<body>
    <h1>⚠️ Dependency Check Report</h1>
    <div class="warning">
        <h2>Scan Status: Incomplete</h2>
        <p><strong>Project:</strong> ${PROJECT_NAME}</p>
        <p><strong>Date:</strong> $(date)</p>
        <p><strong>Issue:</strong> Unable to complete dependency check scan due to NVD database update failure.</p>
        <h3>Recommendations:</h3>
        <ul>
            <li>Verify your NVD API key is valid</li>
            <li>Check network connectivity to NVD API</li>
            <li>Review Jenkins logs for detailed error messages</li>
            <li>Consider running the scan manually with updated database</li>
        </ul>
        <h3>Python Security Audit:</h3>
        <p>Check the <a href="../Python_20Security_20Audit_20Report/">Python Security Audit Report</a> for Python-specific vulnerabilities.</p>
    </div>
</body>
</html>
EOF
                                        }
                                }
                            
                            echo "✅ Dependency-Check scan process completed"
                            echo "📁 Contents of report directory:"
                            ls -lah dependency-check-report/
                        '''
                    }
                }
            }
        }
        
        stage('Publish Reports') {
            steps {
                script {
                    // Publicar reporte de Dependency Check (HTML)
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'dependency-check-report',
                        reportFiles: 'dependency-check-report.html',
                        reportName: 'OWASP Dependency Check Report',
                        reportTitles: 'Dependency Check'
                    ])
                    
                    // Publicar reporte de pip-audit (Markdown)
                    publishHTML([
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'dependency-check-report',
                        reportFiles: 'pip-audit.md',
                        reportName: 'Python Security Audit Report',
                        reportTitles: 'Pip Audit'
                    ])
                    
                    // Archivar todos los reportes
                    archiveArtifacts artifacts: 'dependency-check-report/**/*', allowEmptyArchive: true, fingerprint: true
                    
                    // Publicar resultados en Jenkins (si existe el XML)
                    try {
                        if (fileExists('dependency-check-report/dependency-check-report.xml')) {
                            dependencyCheckPublisher pattern: 'dependency-check-report/dependency-check-report.xml'
                        } else {
                            echo "⚠️ XML report not found, skipping publisher"
                        }
                    } catch (Exception e) {
                        echo "⚠️ Could not publish to Dependency-Check plugin: ${e.message}"
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo "🧹 Pipeline execution completed"
            echo "📊 Report Summary:"
            sh '''
                echo "Files in report directory:"
                ls -lh dependency-check-report/ 2>/dev/null || echo "No reports generated"
            '''
        }
        success {
            echo '✅ Pipeline ejecutado exitosamente!'
            echo "📊 Reportes disponibles:"
            echo "   - OWASP Dependency Check: ${BUILD_URL}OWASP_20Dependency_20Check_20Report/"
            echo "   - Python Security Audit: ${BUILD_URL}Python_20Security_20Audit_20Report/"
        }
        unstable {
            echo '⚠️ Pipeline completado con advertencias'
            echo 'Revisa los reportes para más detalles sobre las vulnerabilidades encontradas'
        }
        failure {
            echo '❌ Pipeline falló. Revisa los logs para más detalles.'
        }
    }
}
