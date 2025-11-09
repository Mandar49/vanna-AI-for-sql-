# ad_ai_app.py
from flask import Flask, jsonify, request, render_template
import pandas as pd
import json
import re
import os

# Import the pre-trained Vanna instance and utility functions
from common import vn
from utils import is_greeting, is_sql_query

# Initialize the Flask application
app = Flask(__name__)

# --- Configuration & Pre-flight Checks ---
CONVERSATIONS_DIR = "conversations"
VANNA_TRAINING_FILE = "vanna_chroma_db/chroma.sqlite3"

if not os.path.exists(CONVERSATIONS_DIR):
    os.makedirs(CONVERSATIONS_DIR)

IS_TRAINED = os.path.exists(VANNA_TRAINING_FILE)
# --- End Configuration ---


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/conversations', methods=['GET'])
def list_conversations():
    try:
        files = os.listdir(CONVERSATIONS_DIR)
        # Sort by modification time, newest first
        files.sort(key=lambda x: os.path.getmtime(os.path.join(CONVERSATIONS_DIR, x)), reverse=True)

        conversations = []
        for filename in files:
            if filename.endswith(".json"):
                filepath = os.path.join(CONVERSATIONS_DIR, filename)
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    # Use the first user message as the title, or a default
                    if data:
                        conversations.append({
                            "id": filename.replace(".json", ""),
                            "title": data[0]['value'] if data and data[0]['role'] == 'user' else 'Untitled'
                        })
        return jsonify(conversations)
    except Exception as e:
        return jsonify({"error": f"Could not list conversations: {e}"}), 500

@app.route('/api/conversations/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    filepath = os.path.join(CONVERSATIONS_DIR, f"{conversation_id}.json")
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return jsonify(json.load(f))
    else:
        return jsonify([]) # Return empty list if no history

def extract_json_from_response(response: str):
    """Safely extracts a JSON object from a string, even with surrounding text."""
    # First, try to find the JSON within markdown-style code blocks
    match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass  # Fall through to the next method

    # If no markdown block, try to parse the whole string
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        # As a last resort, find the first '{' and last '}'
        start = response.find('{')
        end = response.rfind('}') + 1
        if start != -1 and end != 0:
            try:
                return json.loads(response[start:end])
            except json.JSONDecodeError:
                return None  # Failed to extract
    return None

def summarize_data_with_llm(question: str, df: pd.DataFrame) -> str:
    """Uses the LLM to generate a natural language summary of a DataFrame."""
    if df.empty:
        return "I found no data for your question."

    # If the result is a single value, just return it directly.
    if len(df) == 1 and len(df.columns) == 1:
        return f"The answer to your question '{question}' is: {df.iloc[0, 0]}"

    # Otherwise, send to the LLM for a more detailed summary.
    prompt = f"""
    The user asked the following question: '{question}'.
    I ran a SQL query and got the following data:
    {df.to_string()}
    Please summarize this data into a friendly, natural-language sentence.
    Focus on answering the user's original question.
    """
    return vn.submit_prompt([vn.user_message(prompt)])

@app.route('/api/ask', methods=['POST'])
def ask():
    # --- Training Pre-flight Check ---
    if not IS_TRAINED:
        # Return a specific error message if the training file is not found
        return jsonify([{
            "role": "assistant",
            "value": "Error: The AI model has not been trained. Please run `python train.py` from your terminal and then restart the application.",
            "sql": None
        }]), 200 # Return 200 so the frontend displays the message

    data = request.json
    question = data.get('question')
    conversation_id = data.get('conversation_id')

    if not all([question, conversation_id]):
        return jsonify({"error": "Question and conversation_id are required."}), 400

    filepath = os.path.join(CONVERSATIONS_DIR, f"{conversation_id}.json")

    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                chat_history = json.load(f)
        else:
            chat_history = []
    except (json.JSONDecodeError, IOError):
        chat_history = []

    chat_history.append({"role": "user", "value": question})

    # --- Guardrail #1: Greeting Handler ---
    if is_greeting(question):
        chat_history.append({
            "role": "assistant",
            "value": "Hello! I'm your AI assistant for analyzing business data. You can ask me questions about your data, or request strategic analysis. How can I help you today?",
            "sql": None
        })
        with open(filepath, 'w') as f:
            json.dump(chat_history, f, indent=2)
        return jsonify(chat_history)

    # Prepare conversation history for Vanna, keeping the last 4 messages for context
    conversation_for_vanna = [{"role": msg["role"], "content": msg["value"]} for msg in chat_history]
    if len(conversation_for_vanna) > 4:
        conversation_for_vanna = conversation_for_vanna[-4:]

    analytical_keywords = ["analyze", "analyse", "strategy", "improve", "loopholes", "recommend", "suggestions", "breakdown"]

    if any(keyword in question.lower() for keyword in analytical_keywords):
        # --- Brain #2: The "Strategic Analyst Brain" ---
        try:
            deconstruct_prompt = f"""
            Your task is to break down a complex strategic question into a series of smaller, factual sub-questions that can be answered with SQL queries.
            The user's question is: "{question}"
            Respond with ONLY a valid JSON object in the following format: {{"sub_questions": ["question1", "question2", "question3", ...]}}
            """
            llm_response_str = vn.submit_prompt([vn.user_message(deconstruct_prompt)])

            sub_questions_data = extract_json_from_response(llm_response_str)
            sub_questions = sub_questions_data.get("sub_questions", []) if sub_questions_data else []

            facts = []
            for sub_q in sub_questions:
                sql = vn.generate_sql(question=sub_q, chat_history=conversation_for_vanna)
                if sql and is_sql_query(sql):
                    try:
                        df = vn.run_sql(sql)
                        facts.append(f"- For the question '{sub_q}', the data shows: {df.to_string()}\\n")
                    except Exception as e:
                        facts.append(f"- When asking '{sub_q}', I encountered an error: {e}\\n")

            synthesis_prompt = f"""
            The user's original strategic question was: '{question}'.
            I have gathered the following facts by querying the database:
            {''.join(facts)}
            Based ONLY on the facts provided, generate a concise, strategic recommendation.
            Start with a short summary paragraph, then provide a bulleted list of actionable insights.
            """
            final_answer = vn.submit_prompt([vn.user_message(synthesis_prompt)])
            chat_history.append({"role": "assistant", "value": final_answer, "sql": None})

        except Exception as e:
            chat_history.append({"role": "assistant", "value": f"An error occurred during strategic analysis: {e}", "sql": None})

    else:
        # --- Brain #1: The "Data Retrieval Brain" ---
        try:
            sql = vn.generate_sql(question=question, chat_history=conversation_for_vanna)
            print(f"Generated SQL: {sql}")
            
            # --- Guardrail #2: SQL Validation ---
            if sql and is_sql_query(sql):
                try:
                    df = vn.run_sql(sql)
                    summary = summarize_data_with_llm(question, df)
                    chat_history.append({"role": "assistant", "value": summary, "sql": sql})
                except Exception as sql_error:
                    # SQL execution failed
                    error_msg = f"I generated a SQL query but couldn't execute it. Error: {str(sql_error)}"
                    chat_history.append({"role": "assistant", "value": error_msg, "sql": sql})
            else:        
                # If no valid SQL is generated, it's likely a conversational or meta question.
                # Let the base LLM handle it directly without trying to query the database.
                summary = vn.submit_prompt(conversation_for_vanna)
                chat_history.append({"role": "assistant", "value": summary, "sql": None})

        except Exception as e:
            error_msg = f"An error occurred while processing your question: {str(e)}"
            chat_history.append({"role": "assistant", "value": error_msg, "sql": None})

    # Save the updated conversation
    with open(filepath, 'w') as f:
        json.dump(chat_history, f, indent=2)

    return jsonify(chat_history)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
