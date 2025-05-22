# cohere_chatbot.py

import os
import cohere
from app.db import buscar_erro

# Inicializa o cliente Cohere
COHERE_API_KEY = os.getenv("COHERE_API_KEY", "")
co = cohere.Client(COHERE_API_KEY)

# Modelo a usar
COHERE_MODEL = os.getenv("COHERE_MODEL", "command-r-plus")

# Instruções de sistema / persona
SYSTEM_INSTRUCTIONS = (
    "Você é um analista de suporte N1 que presta atendimento respeitoso "
    "e cordial aos clientes e parceiros. Sempre responda de forma clara, objetiva e amigável. "
    "Você trabalha na Zucchetti C4 e presta suporte para os sistemas Desktop ClippPro, ClippService, "
    "ClippCheff, ClippMEI e para os sistemas Web: ZWeb, ClippFacil, Clipp360, ZDesk, MinhasNotas. "
    "Use quebras de linha, parágrafos e listas sempre que fizer sentido para facilitar a leitura."
)

def gerar_resposta_cohere(pergunta: str) -> str:
    # 1) Busca no banco por artigos relacionados à pergunta
    resultado = buscar_erro(pergunta)
    artigos = resultado.get("resultados", [])

    # 2) Monta o contexto para o prompt
    if not artigos:
        prompt = (
            f"{SYSTEM_INSTRUCTIONS}\n\n"
            f"Pergunta: {pergunta}\n\n"
            "Não encontrei nada na base de conhecimento. Responda de forma clara e objetiva."
        )
    else:
        blocos = []
        for art in artigos:
            blocos.append(
                f"Título: {art['titulo']}\n"
                f"Conteúdo: {art['conteudo']}"
            )
        contexto = "\n---\n".join(blocos)

        prompt = (
            f"{SYSTEM_INSTRUCTIONS}\n\n"
            "A seguir, trechos da base de conhecimento interna extraídos do banco de dados:\n\n"
            f"{contexto}\n\n"
            "INSTRUÇÕES:\n"
            "1) Resuma os pontos principais desse conteúdo.\n"
            "2) Informe ao usuário quais procedimentos ele pode seguir para resolver o problema.\n\n"
            f"Pergunta original: {pergunta}"
        )

    # 3) Chama a Cohere para gerar o resumo + resposta
    response = co.generate(
        model=COHERE_MODEL,
        prompt=prompt,
        max_tokens=700,
        temperature=0.7,
        k=0,
        p=0.75,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop_sequences=[]
    )
    resposta_ia = response.generations[0].text.strip()

    # 4) Se encontrou artigos, anexa os links
    if artigos:
        resposta_ia += "\n\n<strong>**Artigos referente ao assunto:**</strong>\n"
        for art in artigos:
            resposta_ia += f"""
{art['titulo']} 
https://suporte.clipp.com.br/artigos/{art['id']}
            """

    return resposta_ia
