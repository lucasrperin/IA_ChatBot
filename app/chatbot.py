import openai
from app.db import buscar_contexto
from config import DB_CONFIG

# Configuração da OpenAI (não esqueça de configurar sua chave API)
openai.api_key = ''

def gerar_resposta(pergunta):
    # Primeiramente, tentamos buscar um contexto relevante no banco de dados
    contexto = buscar_contexto(pergunta)
    
    if "Nenhuma informação encontrada" in contexto:
        # Caso não encontre nada no banco de dados, usamos a IA para buscar uma resposta
        return perguntar_openai(pergunta)

    # Caso tenha encontrado contexto no banco de dados, retornamos a resposta com isso
    return contexto


def perguntar_openai(pergunta):
    # Faz a chamada para a OpenAI usando o GPT-3/4 ou outro modelo que você tiver
    try:
        resposta = openai.Completion.create(
            model="text-davinci-003",  # Ou outro modelo que você preferir
            prompt=pergunta,
            max_tokens=150,
            temperature=0.7,
        )
        return resposta.choices[0].text.strip()
    except Exception as e:
        print(f"[ERRO OPENAI] Não foi possível gerar a resposta: {e}")
        return "Desculpe, ocorreu um erro ao tentar gerar a resposta."
