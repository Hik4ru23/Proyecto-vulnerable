pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build / Install') {
            steps {
                echo 'Instalando dependencias y preparando entorno...'
                sh '''
                    if ! command -v python3 &> /dev/null; then
                        echo "❌ Python3 no está instalado en este agente."
                        exit 1
                    fi

                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    if [ -f requirements.txt ]; then
                        pip install -r requirements.txt
                    else
                        pip install Flask
                    fi
                '''
            }
        }

        stage('Run app (background)') {
            steps {
                sh '''
                    . .venv/bin/activate
                    nohup python3 vulnerable > app.log 2>&1 &
                    echo $! > app.pid
                    sleep 2
                    tail -n 20 app.log || true
                '''
            }
        }

        stage('Smoke test / Hit endpoint') {
            steps {
                sh '''
                    if command -v curl &> /dev/null; then
                        curl --fail --show-error --silent "http://localhost:5000/hello?name=Jenkins" -o response.txt
                        grep -q "Hello" response.txt
                        echo "✅ Smoke test OK"
                    else
                        echo "⚠️ cURL no disponible, omitiendo prueba HTTP"
                    fi
                '''
            }
        }

        stage('Cleanup') {
            steps {
                sh '''
                    if [ -f app.pid ]; then
                        kill $(cat app.pid) || true
                        rm -f app.pid
                    fi
                '''
            }
        }
    }

    post {
        always {
            echo 'Fin del pipeline.'
            sh 'ls -la'
            sh 'cat app.log || true'
        }
        failure {
            echo '❌ Pipeline falló. Revisa los logs.'
        }
    }
}
