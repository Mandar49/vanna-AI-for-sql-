# common.py
import mysql.connector
import pandas as pd
from vanna.ollama.ollama import Ollama
from vanna.qdrant.qdrant_vector import Qdrant_VectorStore
import qdrant_client

# Centralized Configuration
class AppConfig:
    LLM_MODEL = 'gemma:7b'
    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_PASSWORD = ''
    DB_NAME = 'ad_ai_testdb'
    QDRANT_HOST = 'localhost'
    QDRANT_PORT = 6333

# Shared Vanna Class re-architected to use Qdrant
class LocalVanna(Qdrant_VectorStore, Ollama):
    def __init__(self, config=None):
        if config is None:
            config = {}

        # Configure Qdrant connection
        qdrant_client_instance = qdrant_client.QdrantClient(
            host=AppConfig.QDRANT_HOST,
            port=AppConfig.QDRANT_PORT
        )

        # A single, complete config is created and passed to both parent
        # constructors. Each parent will pick the keys it needs.
        full_config = {
            'model': config.get('model', AppConfig.LLM_MODEL),
            'client': qdrant_client_instance,
        }

        Qdrant_VectorStore.__init__(self, config=full_config)
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
