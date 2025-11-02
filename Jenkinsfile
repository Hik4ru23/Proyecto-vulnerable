pipeline {
    // Definimos los "nombres" de las herramientas que configuramos en el Paso 4
    tools {
        org.jenkinsci.plugins.dependencycheck.tools.DependencyCheckInstaller 'DC-Default'
        hudson.plugins.sonar.SonarRunnerInstaller 'SonarScanner-Default'
    }

    agent any

    stages {
        stage('Build') { // <-- ESTE ES EL PASO QUE QUERÍAS
            steps {
                echo 'Instalando dependencias de Python...'
                // ¡ACCIÓN REAL!
                // Ejecuta 'pip' para instalar Flask desde 'requirements.txt'
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Test') {
            steps {
                echo 'Running Unit Tests... (Omitido por ahora)'
            }
        }

        // ... Aquí irían las otras etapas (SonarQube, ZAP, etc.) ...
        // Las he quitado para enfocarnos solo hasta la instalación
        // de dependencias, como pediste.
        // Si quieres el pipeline completo, usa el que te di antes.
    }
}
