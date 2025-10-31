pipeline {
    agent any  // Jenkins puede ejecutarse en cualquier agente o máquina disponible

    stages {
        stage('Build') {
            steps {
                echo 'Compilando el código...'
            }
        }

        stage('Test') {
            steps {
                echo 'Ejecutando pruebas unitarias...'
            }
        }

        stage('Analyze') {
            steps {
                echo 'Analizando la calidad del código con SonarQube...'
            }
        }

        stage('Security Test') {
            steps {
                echo 'Ejecutando OWASP Dependency-Check y ZAP...'
            }
        }

        stage('Deploy') {
            steps {
                echo 'Desplegando la aplicación en un entorno de pruebas...'
            }
        }
    }
}
