import psycopg2
from psycopg2 import sql
import logging
from config import DB_CONFIG

# Configuração de logging
logging.basicConfig(level=logging.DEBUG)

def conectar_banco():
    try:
        # Estabelece a conexão com o banco de dados PostgreSQL
        conn = psycopg2.connect(
            dbname=DB_CONFIG['dbname'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port']
        )
        logging.info("Conexão bem-sucedida com o banco de dados.")
        return conn
    except Exception as e:
        logging.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

def buscar_erro(user_input):
    # Conectar ao banco
    conn = conectar_banco()
    if conn is None:
        return {"error": "Erro ao conectar ao banco de dados"}

    try:
        cur = conn.cursor()

        # Exemplo de uma consulta SQL simples com o `user_input`
        query = sql.SQL("SELECT id, titulo, conteudo FROM artigos WHERE titulo LIKE %s OR conteudo LIKE %s LIMIT 3")
        cur.execute(query, (f"%{user_input}%", f"%{user_input}%"))
        
        artigos = cur.fetchall()
        cur.close()
        conn.close()

        if artigos:
            # Formatar os resultados como uma lista de dicionários
            artigos_list = []
            for artigo in artigos:
                # Forçar a decodificação do conteúdo se necessário
                titulo = artigo[1].decode('utf-8', 'ignore') if isinstance(artigo[1], bytes) else artigo[1]
                conteudo = artigo[2].decode('utf-8', 'ignore') if isinstance(artigo[2], bytes) else artigo[2]
                
                artigos_list.append({
                    'id': artigo[0],
                    'titulo': titulo,
                    'conteudo': conteudo
                })
            return {"resultados": artigos_list}
        else:
            return {"resultados": [], "message": "Nenhum dado encontrado para a sua pergunta."}
    
    except Exception as e:
        logging.error(f"Erro na consulta SQL: {e}")
        return {"error": "Erro ao realizar a consulta no banco de dados."}
