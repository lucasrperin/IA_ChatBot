import psycopg2
from psycopg2 import sql
import logging
from config import DB_CONFIG

logging.basicConfig(level=logging.DEBUG)

def conectar_banco():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        logging.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

def buscar_erro(user_input):
    conn = conectar_banco()
    if not conn:
        return {"error": "Erro ao conectar ao banco de dados"}
    try:
        cur = conn.cursor()
        # 2.1) Full-text search com ranking
        ts_query = sql.SQL("plainto_tsquery('portuguese', %s)")
        query = sql.SQL("""
            SELECT id, titulo, conteudo
            FROM artigos
            WHERE texto_vetor @@ {tsq}
            ORDER BY ts_rank_cd(texto_vetor, {tsq}) DESC
        """).format(tsq=ts_query)
        cur.execute(query, (user_input, user_input))
        artigos = cur.fetchall()

        # 2.2) Fallback para ILIKE caso não ache nada em full-text
        if not artigos:
            pattern = f"%{user_input}%"
            cur.execute("""
                SELECT id, titulo, conteudo
                FROM artigos
                WHERE titulo ILIKE %s OR conteudo ILIKE %s
            """, (pattern, pattern))
            artigos = cur.fetchall()

        cur.close()
        conn.close()

        if not artigos:
            return {"resultados": [], "message": "Nenhum dado encontrado para a sua pergunta."}

        resultados = []
        for art in artigos:
            titulo   = art[1].decode('utf-8','ignore') if isinstance(art[1], bytes) else art[1]
            conteudo = art[2].decode('utf-8','ignore') if isinstance(art[2], bytes) else art[2]
            resultados.append({
                'id': art[0],
                'titulo': titulo,
                'conteudo': conteudo
            })
        return {"resultados": resultados}

    except Exception as e:
        logging.error(f"Erro na consulta SQL: {e}")
        return {"error": "Erro ao realizar a consulta no banco de dados."}
