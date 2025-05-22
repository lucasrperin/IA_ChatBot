# run.py

from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from app.cohere_chatbot import gerar_resposta_cohere

app = Flask(__name__, static_folder='static', static_url_path='/static')

@app.route('/ckeditor_assets/<path:filename>')
def ckeditor_static(filename):
    root = os.path.join(app.root_path, 'ckeditor_assets')
    return send_from_directory(root, filename)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data       = request.json or {}
    pergunta   = data.get('pergunta', '').strip()
    buscar_bdc = data.get('buscarBDC', False)

    if not pergunta:
        return jsonify({'response': 'Por favor, envie uma pergunta válida.'}), 400

    try:
        resposta = gerar_resposta_cohere(pergunta, buscar_bdc)
        return jsonify({'response': resposta})
    except Exception:
        app.logger.exception("Erro no endpoint /chat")
        return jsonify({'response': 'Desculpe, ocorreu um erro interno.'}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
