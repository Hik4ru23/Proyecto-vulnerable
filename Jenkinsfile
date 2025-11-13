pipeline {
    agent any

    environment {
        PROJECT_NAME = "pipeline-test"
        SONARQUBE_URL = "http://sonarqube:9000"
        SONARQUBE_TOKEN = "sqa_77e30137bb8e01768b25a57b9671ad1db4959dcf"
        TARGET_URL = "http://172.23.202.60:5000"
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
                    // Asegúrate de que el nombre coincida con la configuración de Jenkins
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

        stage('Dependency Check') {
    environment {
        NVD_API_KEY = credentials('nvdApiKey')
    }
    steps {
        script {
            // Usar variables de entorno sin interpolación directa en comillas dobles
            def additionalArgs = "--scan . --format HTML --out dependency-check-report --enableExperimental --enableRetired --nvdApiKey ${env.NVD_API_KEY}"
            
            dependencyCheck(
                additionalArguments: additionalArgs,
                odcInstallation: 'DependencyCheck' // Nombre exacto de la instalación
            )
        }
    }
}

        stage('Publish Reports') {
            steps {
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'dependency-check-report',
                    reportFiles: 'dependency-check-report.html',
                    reportName: 'OWASP Dependency Check Report'
                ])
            }
        }
    }
}
