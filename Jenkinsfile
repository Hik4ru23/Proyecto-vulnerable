pipeline {
    agent any
    
    environment {
        PROJECT_NAME = "pipeline-test"
        SONARQUBE_URL = "http://sonarqube:9000"
        SONARQUBE_TOKEN = "sqa_77e30137bb8e01768b25a57b9671ad1db4959dcf"
        TARGET_URL = "http://172.23.202.60:5000"
        DC_VERSION = "10.0.4"
        DC_DIRECTORY = "${WORKSPACE}/dependency-check"
        DC_DATA_DIRECTORY = "/var/jenkins_home/dependency-check-data"
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
                    
                    echo "🐍 Installing dependencies..."
                    // Llama a pip directamente desde el venv
                    venv/bin/pip install --break-system-packages -r requirements.txt
                    
                    echo "🐍 Installing security tools..."
                    // Instala las herramientas de auditoría en el mismo venv
                    venv/bin/pip install --break-system-packages pip-audit safety
                '''
            }
        }
        
        stage('Python Security Audit') {
            steps {
                sh '''
                    mkdir -p dependency-check-report
                    
                    echo "🔍 Running pip-audit..."
                    // Llama a pip-audit directamente desde el venv
                    venv/bin/pip-audit -r requirements.txt -f markdown -o dependency-check-report/pip-audit.md || true
                    venv/bin/pip-audit -r requirements.txt -f json -o dependency-check-report/pip-audit.json || true
                    
                    echo "🔍 Running safety check..."
                    // Llama a safety directamente desde el venv
                    venv/bin/safety check -r requirements.txt --json > dependency-check-report/safety-report.json || true
                    venv/bin/safety check -r requirements.txt > dependency-check-report/safety-report.txt || true
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
                        
                        # Crear directorio de datos persistente
                        mkdir -p ${DC_DATA_DIRECTORY}
                        
                        if [ ! -d "${DC_DIRECTORY}/dependency-check" ]; then
                            mkdir -p ${DC_DIRECTORY}
                            cd ${DC_DIRECTORY}
                            echo "Downloading Dependency-Check ${DC_VERSION}..."
                            wget -q https://github.com/jeremylong/DependencyCheck/releases/download/v${DC_VERSION}/dependency-check-${DC_VERSION}-release.zip
                            unzip -q dependency-check-${DC_VERSION}-release.zip
                            chmod +x dependency-check/bin/dependency-check.sh
                            rm dependency-check-${DC_VERSION}-release.zip
                            echo "✅ Dependency-Check installed"
                        else
                            echo "✅ Dependency-Check already installed"
                        fi
                    '''
                }
            }
        }
        
        stage('Dependency Check Scan') {
            steps {
                withCredentials([string(credentialsId: 'nvdApiKey', variable: 'NVD_API_KEY')]) {
                    script {
                        sh '''
                            echo "🔍 Running Dependency-Check scan with NVD updates..."
                            mkdir -p dependency-check-report
                            
                            # Verificar que el API key no esté vacío
                            if [ -z "${NVD_API_KEY}" ]; then
                                echo "❌ ERROR: NVD API Key is empty!"
                                exit 1
                            fi
                            
                            echo "✓ API Key configured (length: ${#NVD_API_KEY} characters)"
                            
                            # Ejecutar el scan con el API key
                            ${DC_DIRECTORY}/dependency-check/bin/dependency-check.sh \
                                --scan . \
                                --exclude "**/venv/**" \
                                --exclude "**/dependency-check/**" \
                                --exclude "**/.git/**" \
                                --exclude "**/node_modules/**" \
                                --format HTML \
                                --format JSON \
                                --format XML \
                                --format JUNIT \
                                --out dependency-check-report \
                                --data ${DC_DATA_DIRECTORY} \
                                --project "${PROJECT_NAME}" \
                                --nvdApiKey "${NVD_API_KEY}" \
                                --nvdApiDelay 8000 \
                                --nvdMaxRetryCount 15 \
                                --nvdValidForHours 24 \
                                --enableExperimental \
                                --enableRetired \
                                --prettyPrint \
                                --log dependency-check-report/dependency-check.log || {
                                    echo "⚠️ Scan completed with warnings or vulnerabilities found"
                                    echo "Check the logs at: dependency-check-report/dependency-check.log"
                                }
                            
                            echo "✅ Dependency-Check scan completed"
                            echo ""
                            echo "📁 Generated files:"
                            ls -lh dependency-check-report/
                        '''
                    }
                }
            }
        }
        
        stage('Generate Dashboard') {
            steps {
                script {
                    sh '''
                        cat > dependency-check-report/index.html <<'HTMLEOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security Scan Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }
        .header h1 {
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            animation: fadeInDown 0.6s ease;
        }
        .header p {
            font-size: 1.2em;
            opacity: 0.95;
            animation: fadeInUp 0.6s ease 0.2s both;
        }
        .reports-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }
        .report-card {
            background: white;
            border-radius: 20px;
            padding: 35px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.2);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            animation: fadeInUp 0.6s ease both;
        }
        .report-card:nth-child(1) { animation-delay: 0.1s; }
        .report-card:nth-child(2) { animation-delay: 0.2s; }
        .report-card:nth-child(3) { animation-delay: 0.3s; }
        .report-card:hover {
            transform: translateY(-15px) scale(1.02);
            box-shadow: 0 20px 50px rgba(0,0,0,0.3);
        }
        .report-card .icon {
            font-size: 4em;
            margin-bottom: 20px;
            display: block;
            animation: bounce 2s infinite;
        }
        .report-card h2 {
            color: #333;
            margin-bottom: 15px;
            font-size: 1.6em;
        }
        .report-card p {
            color: #666;
            line-height: 1.8;
            margin-bottom: 25px;
            font-size: 1.05em;
        }
        .report-card .button {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 35px;
            border-radius: 30px;
            text-decoration: none;
            font-weight: 700;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .report-card .button:hover {
            transform: scale(1.05);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
        }
        .info-box {
            background: white;
            border-radius: 20px;
            padding: 35px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.2);
            animation: fadeInUp 0.6s ease 0.4s both;
        }
        .info-box h3 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.5em;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        .info-box ul {
            list-style: none;
            color: #666;
        }
        .info-box li {
            padding: 15px 0;
            border-bottom: 1px solid #f0f0f0;
            font-size: 1.05em;
        }
        .info-box li:last-child { border-bottom: none; }
        .info-box li strong {
            color: #667eea;
            font-weight: 700;
        }
        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ Security Scan Dashboard</h1>
            <p>Comprehensive Security Analysis Results</p>
        </div>
        
        <div class="reports-grid">
            <div class="report-card">
                <span class="icon">🔍</span>
                <h2>OWASP Dependency Check</h2>
                <p>Comprehensive vulnerability analysis detecting known CVEs in project dependencies with detailed remediation guidance.</p>
                <a href="dependency-check-report.html" class="button">View Full Report →</a>
            </div>
            
            <div class="report-card">
                <span class="icon">🐍</span>
                <h2>Python Security Audit</h2>
                <p>Python-specific vulnerability scanning using pip-audit to identify security issues in Python packages and dependencies.</p>
                <a href="pip-audit.md" class="button">View Audit →</a>
            </div>
            
            <div class="report-card">
                <span class="icon">🔒</span>
                <h2>Safety Check Report</h2>
                <p>Additional security validation using Safety database for comprehensive Python package vulnerability detection.</p>
                <a href="safety-report.txt" class="button">View Safety Report →</a>
            </div>
        </div>
        
        <div class="info-box">
            <h3>📊 Scan Information</h3>
            <ul>
                <li><strong>Scan Date:</strong> $(date)</li>
                <li><strong>Project:</strong> ${PROJECT_NAME}</li>
                <li><strong>Build:</strong> #${BUILD_NUMBER}</li>
                <li><strong>Job:</strong> ${JOB_NAME}</li>
                <li><strong>NVD Database:</strong> Updated with API Key</li>
            </ul>
        </div>
    </div>
</body>
</html>
HTMLEOF
                    '''
                }
            }
        }
        
        stage('Publish Reports') {
            steps {
                script {
                    // Dashboard principal
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'dependency-check-report',
                        reportFiles: 'index.html',
                        reportName: '🛡️ Security Dashboard',
                        reportTitles: 'Security Dashboard'
                    ])
                    
                    // Reporte OWASP
                    publishHTML([
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'dependency-check-report',
                        reportFiles: 'dependency-check-report.html',
                        reportName: '📊 OWASP Dependency Check',
                        reportTitles: 'OWASP Report'
                    ])
                    
                    // Archivar artifacts
                    archiveArtifacts artifacts: 'dependency-check-report/**/*', allowEmptyArchive: true, fingerprint: true
                    
                    // JUNIT results
                    try {
                        junit allowEmptyResults: true, testResults: 'dependency-check-report/dependency-check-junit.xml'
                    } catch (Exception e) {
                        echo "⚠️ JUnit results not published: ${e.message}"
                    }
                    
                    // Plugin de Dependency Check
                    try {
                        if (fileExists('dependency-check-report/dependency-check-report.xml')) {
                            dependencyCheckPublisher pattern: 'dependency-check-report/dependency-check-report.xml'
                        }
                    } catch (Exception e) {
                        echo "⚠️ Dependency-Check plugin: ${e.message}"
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo "🧹 Cleaning up and generating summary..."
            script {
                sh '''
                    echo ""
                    echo "═══════════════════════════════════════"
                    echo "              📊 SCAN SUMMARY"
                    echo "═══════════════════════════════════════"
                    echo ""
                    
                    if [ -f dependency-check-report/dependency-check-report.json ]; then
                        echo "✅ OWASP Dependency Check: COMPLETED"
                    else
                        echo "❌ OWASP Dependency Check: FAILED"
                    fi
                    
                    if [ -f dependency-check-report/pip-audit.json ]; then
                        echo "✅ Python Pip Audit: COMPLETED"
                    else
                        echo "⚠️  Python Pip Audit: INCOMPLETE"
                    fi
                    
                    if [ -f dependency-check-report/safety-report.json ]; then
                        echo "✅ Safety Check: COMPLETED"
                    else
                        echo "⚠️  Safety Check: INCOMPLETE"
                    fi
                    
                    echo ""
                    echo "📁 Generated Files:"
                    ls -lh dependency-check-report/ | grep -v "^total" | awk '{print "    " $9 " (" $5 ")"}'
                    echo ""
                    echo "═══════════════════════════════════════"
                '''
            }
        }
        success {
            echo '✅ ═══════════════════════════════════════'
            echo '✅  PIPELINE COMPLETADO EXITOSAMENTE'
            echo '✅ ═══════════════════════════════════════'
            echo ''
            echo "📊 Reportes disponibles en:"
            echo "   🛡️  Security Dashboard: ${BUILD_URL}Security_20Dashboard/"
            echo "   📊 OWASP Report: ${BUILD_URL}OWASP_20Dependency_20Check/"
            echo ''
        }
        unstable {
            echo '⚠️  ═══════════════════════════════════════'
            echo '⚠️   VULNERABILIDADES DETECTADAS'
            echo '⚠️  ═══════════════════════════════════════'
            echo 'Revisa los reportes para detalles y recomendaciones'
        }
        failure {
            echo '❌ ═══════════════════════════════════════'
            echo '❌  PIPELINE FALLÓ'
            echo '❌ ═══════════════════════════════════════'
            echo 'Revisa los logs para identificar el problema'
        }
    }
}
