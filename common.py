# common.py
import mysql.connector
import pandas as pd
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore
from vanna.ollama.ollama import Ollama

# --- Centralized Configuration ---
class AppConfig:
    # Vanna expects the model name in a specific format.
    # The 'gemma:7b' part is the model identifier for Ollama.
    # The 'local' part is a placeholder for the Vanna API key, which we don't need for a local setup.
    VANNA_MODEL = 'gemma:7b'

    # Database connection details
    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_PASSWORD = ''
    DB_NAME = 'ad_ai_testdb'

    # Path for the local ChromaDB vector store file
    CHROMA_DB_PATH = 'vanna_chroma_db'

# --- Vanna Setup ---
# This custom class inherits from both the ChromaDB vector store and the Ollama LLM connector.
# This is the standard Vanna pattern for creating a 100% local, file-based instance.
class LocalVanna(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        if config is None:
            config = {}

        # A single, complete config object is created and passed to both parent constructors.
        # Each parent class will pick the keys it needs from this config.
        # This ensures the 'model' is passed to Ollama and the 'path' is passed to ChromaDB.
        full_config = {
            'model': AppConfig.VANNA_MODEL,
            'path': AppConfig.CHROMA_DB_PATH,
        }

        ChromaDB_VectorStore.__init__(self, config=full_config)
        Ollama.__init__(self, config=full_config)

# --- Shared Vanna Instance ---
# This single instance will be imported and used by both train.py and ad_ai_app.py
# This ensures that the app uses the same pre-trained instance that the training script creates.
vn = LocalVanna()

# --- Shared Database Connection Function ---
def run_sql(sql: str) -> pd.DataFrame:
    """
    A shared function to execute SQL queries against the MySQL database.
    This function will be assigned to the vanna instance.
    """
    conn = mysql.connector.connect(
        host=AppConfig.DB_HOST,
        user=AppConfig.DB_USER,
        password=AppConfig.DB_PASSWORD,
        database=AppConfig.DB_NAME
    )
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df

# Assign the database connection function to our Vanna instance
vn.run_sql = run_sql
