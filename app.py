from flask import Flask, request, jsonify
from flask_cors import CORS # ESTO ES NUEVO
from analizador import analizar_ticket_ocr

app = Flask(__name__)
CORS(app) # ESTO PERMITE QUE NETLIFY SE CONECTE A ESTE MOTOR

@app.route('/')
def inicio():
    return "Motor de Premium Hospital en línea."

@app.route('/procesar_ticket', methods=['POST'])
def procesar_ticket():
    datos = request.json
    texto_crudo = datos.get('texto_ocr', '')
    resultados_limpios = analizar_ticket_ocr(texto_crudo)
    return jsonify(resultados_limpios)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

# 1. LA PÁGINA DE INICIO
@app.route('/')
def inicio():
    return """
    <h1>Servidor de Premium Hospital Funcionando 🏥</h1>
    <p>El motor de análisis está en línea y esperando imágenes.</p>
    <p><i>(Aquí el informático conectará la interfaz visual de subida de fotos y el informe.html)</i></p>
    """

# 2. EL CANAL DE COMUNICACIÓN (API)
@app.route('/procesar_ticket', methods=['POST'])
def procesar_ticket():
    # Recibimos el texto que ha leído el OCR desde la página web
    datos = request.json
    texto_crudo = datos.get('texto_ocr', '')
    
    # Pasamos el texto por TU MOTOR (el archivo analizador.py)
    resultados_limpios = analizar_ticket_ocr(texto_crudo)
    
    # Devolvemos los datos listos para mostrar en la pantalla de verificación
    return jsonify(resultados_limpios)

if __name__ == '__main__':
    # Encendemos el servidor en el puerto 5000
    print("Iniciando el servidor de Premium Hospital...")
    app.run(debug=True, port=5000)