## @package vulnerable_server
#  Documentación del servidor vulnerable.
#  
#  Este módulo levanta una aplicación web simple utilizando Flask.
#  Fue diseñado intencionalmente con vulnerabilidades para probar herramientas de seguridad
#  como OWASP Dependency Check y análisis estático.

from flask import Flask, request

## Instancia principal de la aplicación Flask.
app = Flask(__name__)

## @brief Página de inicio (Root).
#  @details Esta función maneja la ruta raíz '/' y devuelve un mensaje de texto plano.
#  No requiere parámetros y es segura por defecto.
#  @return Un string con el mensaje "Welcome to the vulnerable app!".
@app.route('/')
def index():
    return "Welcome to the vulnerable app!"


## @brief Endpoint de saludo (Vulnerable a XSS).
#  @details Esta función toma un parámetro de la URL y lo devuelve en la respuesta.
#  @warning **VULNERABILIDAD:** Este endpoint es vulnerable a Cross-Site Scripting (XSS) Reflejado.
#  El parámetro 'name' no es saneado ni escapado antes de ser devuelto al navegador.
#  @param name El nombre que el usuario envía en la petición GET (ej: /hello?name=Gonzalo).
#  @return Un string formateado con el saludo.
@app.route('/hello', methods=['GET'])
def hello():
    name = request.args.get('name')
    return f'Hello, {name}!'

## @brief Bloque principal de ejecución.
#  @details Inicia el servidor web en el puerto 5000.
#  Se configura en host '0.0.0.0' para ser visible fuera del contenedor Docker.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
