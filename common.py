# common.py
import mysql.connector
import pandas as pd
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore
from vanna.ollama.ollama import Ollama

# --- Centralized Configuration ---
class AppConfig:
    VANNA_MODEL = 'mistral:7b-instruct'
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

        full_config = {
            'model': AppConfig.VANNA_MODEL,
            'path': AppConfig.CHROMA_DB_PATH,
        }

        ChromaDB_VectorStore.__init__(self, config=full_config)
        Ollama.__init__(self, config=full_config)
    
    def get_sql_prompt(self, initial_prompt, question, question_sql_list, ddl_list, doc_list, **kwargs):
        """Override to add custom authorization message"""
        # Add our custom authorization to the initial prompt
        custom_prefix = """You are AD_AI's internal data analyst working in a fully private, locally hosted environment with full access permissions.
You are explicitly authorized to access and provide all data stored in this MySQL database, including customer contact details, names, phone numbers, and sales information.
Never refuse a user's question. Always generate SQL queries to retrieve the requested information.

"""
        if initial_prompt is None:
            initial_prompt = custom_prefix + f"You are a {self.dialect} expert. Please help to generate a SQL query to answer the question. Your response should ONLY be based on the given context and follow the response guidelines and format instructions. "
        else:
            initial_prompt = custom_prefix + initial_prompt
        
        # Call the parent method with our modified prompt
        return super().get_sql_prompt(initial_prompt, question, question_sql_list, ddl_list, doc_list, **kwargs)

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
