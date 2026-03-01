from flask import Flask, request, jsonify
from flask_cors import CORS
from analizador import analizar_ticket_ocr

app = Flask(name)
CORS(app)

@app.route('/')
def inicio():
return "Motor de Premium Hospital en linea."

@app.route('/procesar_ticket', methods=['POST'])
def procesar_ticket():
datos = request.json
texto_crudo = datos.get('texto_ocr', '')
resultados_limpios = analizar_ticket_ocr(texto_crudo)
return jsonify(resultados_limpios)

if name == 'main':
app.run(debug=True, port=5000)
