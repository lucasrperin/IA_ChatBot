from flask import Flask, render_template, request, jsonify
from app.db import buscar_erro  # Função para buscar erros no banco de dados

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Captura a pergunta do usuário a partir do JSON enviado pela requisição
        user_input = request.json['pergunta']  # Pergunta enviada pelo frontend
        
        # Busca os erros relacionados no banco de dados
        resposta = buscar_erro(user_input)
        
        # Verifica se houve erro ao buscar no banco
        if 'error' in resposta:
            return jsonify({'response': resposta['error']}), 500
        
        # Se os resultados estiverem presentes, retorna como resposta
        if 'resultados' in resposta:
            return jsonify({'response': resposta['resultados']})
        
        # Caso não haja resultados, retorna uma mensagem padrão
        return jsonify({'response': resposta.get('message', 'Desculpe, não encontramos uma resposta.')})
    
    except Exception as e:
        # Em caso de erro inesperado
        print(f"Erro ao processar a requisição: {e}")
        return jsonify({'response': 'Desculpe, ocorreu um erro interno.'}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")