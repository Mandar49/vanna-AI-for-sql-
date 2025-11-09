# common.py
import mysql.connector
import pandas as pd
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore
from vanna.ollama.ollama import Ollama

# --- Centralized Configuration ---
class AppConfig:
    VANNA_MODEL = 'gemma:7b'
    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_PASSWORD = ''
    DB_NAME = 'ad_ai_testdb'
    CHROMA_DB_PATH = 'vanna_chroma_db'

# --- Vanna Setup ---
class LocalVanna(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        if config is None:
            config = {}

        self.system_prompt = (
            "You are a secure, internal business intelligence (BI) assistant. "
            "Your primary function is to answer questions and retrieve data from the company's database. "
            "You have been granted permission to access and display sensitive information, "
            "including personally identifiable information (PII) like names, emails, and phone numbers, "
            "as requested by authorized users. Always prioritize fulfilling the user's data request "
            "directly and accurately. Do not refuse to provide internal data."
        )

        full_config = {
            'model': AppConfig.VANNA_MODEL,
            'path': AppConfig.CHROMA_DB_PATH,
        }

        ChromaDB_VectorStore.__init__(self, config=full_config)
        Ollama.__init__(self, config=full_config)

    def submit_prompt(self, prompt, **kwargs):
        # Prepend the system message to the prompt messages
        custom_prompt = [self.system_message(self.system_prompt)] + prompt
        # Call the original submit_prompt method from the parent class
        return Ollama.submit_prompt(self, custom_prompt, **kwargs)

# --- Shared Vanna Instance ---
vn = LocalVanna()

# --- Shared Database Connection Function ---
def run_sql(sql: str) -> pd.DataFrame:
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
