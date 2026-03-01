from flask import Flask, request, jsonify
from flask_cors import CORS
from analizador import analizar_ticket_ocr
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def inicio():
    return "Motor de Premium Hospital funcionando."

@app.route('/procesar_ticket', methods=['POST'])
def procesar_ticket():
    datos = request.json
    texto_crudo = datos.get('texto_ocr', '')
    resultados_limpios = analizar_ticket_ocr(texto_crudo)
    return jsonify(resultados_limpios)

if __name__ == '__main__':
    puerto = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=puerto)
