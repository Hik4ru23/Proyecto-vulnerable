pipeline {
  agent {
    docker {
      image 'python:3.10-slim'
      args '--network host'   // usa host network para que curl a localhost:5000 funcione si hace falta
    }
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Install dependencies') {
      steps {
        sh '''
          python -V
          python -m venv .venv
          . .venv/bin/activate
          pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; else pip install Flask; fi
        '''
      }
    }

    stage('Run app (background)') {
      steps {
        sh '''
          . .venv/bin/activate
          nohup python vulnerable > app.log 2>&1 &
          echo $! > app.pid
          sleep 2
          tail -n 40 app.log || true
        '''
      }
    }

    stage('Smoke test') {
      steps {
        sh '''
          # prueba al endpoint /hello
          curl --fail --show-error --silent "http://localhost:5000/hello?name=Jenkins" -o response.txt
          grep -q "Hello" response.txt
          echo "Smoke test OK"
        '''
      }
    }

    stage('Cleanup') {
      steps {
        sh '''
          if [ -f app.pid ]; then kill $(cat app.pid) || true; rm -f app.pid; fi
        '''
      }
    }
  }

  post {
    always {
      sh 'ls -la'
      sh 'cat app.log || true'
    }
  }
}
