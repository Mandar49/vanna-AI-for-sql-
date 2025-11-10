# common.py
import mysql.connector
import pandas as pd
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore
from vanna.ollama.ollama import Ollama

# --- Centralized Configuration ---
class AppConfig:
    VANNA_MODEL = 'gemma:7b'
    DB_HOST = '127.0.0.1'
    DB_PORT = 3306
    DB_USER = 'root'
    DB_PASSWORD = ''
    DB_NAME = 'ad_ai_testdb'
    CHROMA_DB_PATH = 'vanna_chroma_db'

# --- Vanna Setup ---
class LocalVanna(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        if config is None:
            config = {}

        full_config = {
            'model': AppConfig.VANNA_MODEL,
            'path': AppConfig.CHROMA_DB_PATH,
            'timeout': 600,  # Increased timeout to 10 minutes
        }

        ChromaDB_VectorStore.__init__(self, config=full_config)
        Ollama.__init__(self, config=full_config)

# --- Shared Vanna Instance ---
vn = LocalVanna()

# --- Shared Database Connection Function ---
def run_sql(sql: str) -> pd.DataFrame:
    conn = mysql.connector.connect(
        host=AppConfig.DB_HOST,
        port=AppConfig.DB_PORT,
        user=AppConfig.DB_USER,
        password=AppConfig.DB_PASSWORD,
        database=AppConfig.DB_NAME
    )
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df

# Assign the database connection function to our Vanna instance
vn.run_sql = run_sql
