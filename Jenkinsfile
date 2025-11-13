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
                                -Dsonar.login=${SONARQUBE_TOKEN}
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
                            
                            ${DC_DIRECTORY}/dependency-check/bin/dependency-check.sh \
                                --scan . \
                                --format HTML \
                                --format JSON \
                                --format XML \
                                --out dependency-check-report \
                                --enableExperimental \
                                --enableRetired \
                                --nvdApiKey ${NVD_API_KEY} \
                                --suppression suppression.xml || true
                            
                            echo "✅ Dependency-Check scan completed"
                            ls -la dependency-check-report/
                        '''
                    }
                }
            }
        }
        
        stage('Publish Reports') {
            steps {
                // Publicar reporte de Dependency Check
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'dependency-check-report',
                    reportFiles: 'dependency-check-report.html',
                    reportName: 'OWASP Dependency Check Report'
                ])
                
                // Publicar reporte de pip-audit
                publishHTML([
                    allowMissing: true,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'dependency-check-report',
                    reportFiles: 'pip-audit.md',
                    reportName: 'Python Security Audit Report'
                ])
                
                // Archivar todos los reportes
                archiveArtifacts artifacts: 'dependency-check-report/**/*', allowEmptyArchive: true
                
                // Publicar resultados en Jenkins (si tienes el plugin instalado)
                script {
                    try {
                        dependencyCheckPublisher pattern: 'dependency-check-report/dependency-check-report.xml'
                    } catch (Exception e) {
                        echo "⚠️ Could not publish to Dependency-Check plugin: ${e.message}"
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo "🧹 Cleaning up..."
        }
        success {
            echo '✅ Pipeline ejecutado exitosamente!'
            echo "📊 Reportes disponibles:"
            echo "   - OWASP Dependency Check"
            echo "   - Python Security Audit"
        }
        failure {
            echo '❌ Pipeline falló. Revisa los logs para más detalles.'
        }
    }
}
