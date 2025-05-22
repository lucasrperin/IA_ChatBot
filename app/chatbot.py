import os
import logging
import openai
from app.db import buscar_erro   # ou from db import buscar_erro, conforme seu layout
from dotenv import load_dotenv
from config import DB_CONFIG

load_dotenv()  # carrega o .env
openai.api_key = ""

if not openai.api_key:
    raise RuntimeError("OPENAI_API_KEY não definido – verifique seu .env ou variável de ambiente")

logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

SYSTEM_PROMPT = (
    "Você é um analista de suporte N1 que presta atendimento "
    "respeitoso e cordial aos clientes e parceiros. "
    "Responda de forma clara, objetiva e amigável."
)

def gerar_resposta(pergunta: str) -> str:
    resultado = buscar_erro(pergunta)
    if 'error' in resultado:
        return "Desculpe, não consegui acessar a base de conhecimento agora."

    artigos = resultado.get('resultados', [])
    if not artigos:
        prompt = f"{pergunta}\n\nResponda de forma clara e objetiva."
    else:
        blocos = []
        for a in artigos:
            blocos.append(
                f"Título: {a['titulo']}\n"
                f"Conteúdo: {a['conteudo']}\n"
            )
        contexto = "\n---\n".join(blocos)
        prompt = (
            "A seguir você tem trechos da base de conhecimento interna.\n\n"
            f"{contexto}\n\n"
            "INSTRUÇÕES:\n"
            "1) Resuma em até 3 frases o que há nesse contexto, sem copiar o texto inteiro.\n"
            "2) Em seguida, responda à pergunta abaixo de forma objetiva.\n\n"
            f"Pergunta: {pergunta}"
        )

    return _chamar_openai(prompt)


def _chamar_openai(conteudo: str) -> str:
    try:
        resp = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": conteudo},
            ],
            max_tokens=350,
            temperature=0.7,
        )
        return resp.choices[0].message.content.strip()

    except Exception as e:
        logging.exception("Erro ao chamar OpenAI")
        err = str(e).lower()
        if "insufficient_quota" in err:
            return (
                "Não foi possível gerar a resposta: cota insuficiente na sua conta OpenAI. "
                "Verifique seu plano em platform.openai.com."
            )
        if "429" in err or "rate limit" in err:
            return "O serviço está sobrecarregado. Tente novamente em alguns instantes."
        return f"Desculpe, ocorreu um erro ao gerar a resposta: {e}"