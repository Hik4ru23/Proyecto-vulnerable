pipeline {
    agent {
        docker {
            // Imagen base con Python y Java (para Dependency-Check)
            image 'python:3.10-slim'
            args '-u root' // Ejecuta como root para instalar herramientas si es necesario
        }
    }

    environment {
        APP_NAME = 'vulnerable.py'
        REPORTS_DIR = 'reports'
        DEP_CHECK_VERSION = '10.0.3'
    }

    stages {

        stage('Checkout') {
            steps {
                echo '📦 Clonando repositorio...'
                checkout scm
            }
        }

        stage('Setup Environment') {
            steps {
                echo '⚙️ Instalando dependencias del sistema...'
                sh '''
                    apt-get update -y
                    apt-get install -y openjdk-17-jdk curl unzip
                    ln -s /usr/bin/python3 /usr/bin/python || true
                '''
                echo '📦 Instalando dependencias del proyecto...'
                sh 'pip install --no-cache-dir -r requirements.txt || true'
            }
        }

        stage('Static Analysis - Dependency Check (SCA)') {
            steps {
                echo '🔍 Ejecutando OWASP Dependency-Check...'
                sh '''
                    mkdir -p /opt/dependency-check ${REPORTS_DIR}
                    cd /opt/dependency-check
                    curl -L -o dependency-check.zip https://github.com/jeremylong/DependencyCheck/releases/download/v${DEP_CHECK_VERSION}/dependency-check-${DEP_CHECK_VERSION}-release.zip
                    unzip -o dependency-check.zip
                    chmod +x dependency-check/bin/dependency-check.sh
                    dependency-check/bin/dependency-check.sh \
                        --project "Proyecto Vulnerable" \
                        --scan /var/jenkins_home/workspace/Pipeline \
                        --format "HTML" \
                        --out /var/jenkins_home/workspace/Pipeline/${REPORTS_DIR} \
                        --enableExperimental
                '''
            }
            post {
                always {
                    echo '📁 Archivando reporte de Dependency-Check...'
                    archiveArtifacts artifacts: '**/reports/*.html', allowEmptyArchive: true
                }
            }
        }

        stage('Run App') {
            steps {
                echo '🚀 Iniciando la aplicación Flask...'
                sh '''
                    nohup python ${APP_NAME} &
                    sleep 5
                    echo "✅ Aplicación iniciada en http://localhost:5000"
                '''
            }
        }

        stage('Dynamic Analysis - OWASP ZAP (DAST)') {
            steps {
                echo '🕷️ Ejecutando OWASP ZAP Baseline Scan...'
                sh '''
                    curl -O https://raw.githubusercontent.com/zaproxy/zaproxy/main/docker/zap-baseline.py
                    chmod +x zap-baseline.py
                    ./zap-baseline.py \
                        -t http://localhost:5000/hello?name=test \
                        -p 8090 \
                        -J zap-baseline-report.json
                '''
            }
            post {
                always {
                    echo '📁 Archivando reporte de ZAP...'
                    archiveArtifacts artifacts: 'zap-baseline-report.json', allowEmptyArchive: true
                }
            }
        }
    }

    post {
        always {
            echo '🧹 Limpiando procesos...'
            sh 'pkill -f "python vulnerable.py" || true'
            echo '✅ Pipeline finalizado correctamente.'
        }
    }
}
