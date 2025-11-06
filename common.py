# common.py
import mysql.connector
import pandas as pd
from vanna.ollama.ollama import Ollama
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore

# Centralized Configuration
class AppConfig:
    LLM_MODEL = 'gemma:7b'
    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_PASSWORD = ''
    DB_NAME = 'ad_ai_testdb'
    CHROMA_DB_PATH = './vanna_chroma_db'

# Shared Vanna Class with the CORRECT inheritance and __init__ pattern.
# This inherits from both the VectorStore and LLM components, which is the
# library's intended pattern for creating a local-only Vanna instance.
class LocalVanna(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        if config is None:
            config = {}

        # A single, complete config is created and passed to both parent
        # constructors. Each parent will pick the keys it needs. This
        # ensures the 'model' key is passed to the Ollama parent, fixing the bug.
        full_config = {
            'model': config.get('model', AppConfig.LLM_MODEL),
            'path': config.get('path', AppConfig.CHROMA_DB_PATH),
        }

        ChromaDB_VectorStore.__init__(self, config=full_config)
        Ollama.__init__(self, config=full_config)

# Shared Database Connection Function
def run_sql(sql: str) -> pd.DataFrame:
    conn = mysql.connector.connect(
        host=AppConfig.DB_HOST,
        user=AppConfig.DB_USER,
        password=AppConfig.DB_PASSWORD,
        database=AppConfig.DB_NAME
    )
    return pd.read_sql_query(sql, conn)
