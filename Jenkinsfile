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
          # crear venv para aislamiento (si no existe python3, ajustar)
          python3 -m venv .venv
          . .venv/bin/activate
          pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; else pip install Flask; fi
        '''
      }
    }

    stage('Run app (background)') {
      steps {
        echo 'Lanzando la app Flask en background...'
        sh '''
          . .venv/bin/activate
          # ejecutar la app en background y guardar PID
          nohup python app.py > app.log 2>&1 &
          echo $! > app.pid
          sleep 2
          # mostrar las primeras líneas del log (útil para debugging rápido)
          head -n 40 app.log || true
        '''
      }
    }

    stage('Smoke test / Hit endpoint') {
      steps {
        echo 'Probando endpoint /hello (smoke test)...'
        sh '''
          # Probar endpoint; si corre en contenedor Jenkins en Docker, puede necesitar host.docker.internal
          # aquí asumimos que la app está expuesta en el mismo host: http://localhost:5000
          set +e
          curl --max-time 5 "http://localhost:5000/hello?name=Jenkins" -s -o response.txt -w "%{http_code}"
          RC=$?
          if [ $RC -ne 0 ]; then
            echo "curl falló (código de salida $RC)"
            cat response.txt || true
            exit 1
          fi
          HTTP_CODE=$(tail -n1 response.txt)
          # Si curl devolvió la respuesta, response.txt contiene body; aquí validamos que contenga 'Hello'
          if ! grep -q "Hello" response.txt; then
            echo "Respuesta inesperada:"
            cat response.txt
            exit 1
          fi
          echo "Smoke test OK"
        '''
      }
    }

    stage('Cleanup') {
      steps {
        echo 'Deteniendo la app y limpiando...'
        sh '''
          if [ -f app.pid ]; then
            kill $(cat app.pid) || true
            rm -f app.pid
          fi
          # desactivar venv (no necesario en script), opcional limpiar logs
          # rm -rf .venv
        '''
      }
    }
  }

  post {
    always {
      echo 'Fin del pipeline.'
      sh 'ls -la || true'
    }
  }
}
