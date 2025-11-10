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
VANNA_TRAINING_FILE = "vanna-chroma.sqlite3"

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

def summarize_data_with_llm(question: str, df: pd.DataFrame, conversation_history: list) -> str:
    """Uses the LLM to generate a natural language summary of a DataFrame."""
    if df.empty:
        return "I found no data for your question."

    # Always send to the LLM for a more detailed summary.
    summary_prompt = f"""
    The user's question was: '{question}'.
    I executed a SQL query and retrieved the following data:
    ---
    {df.to_string()}
    ---
    Your task is to act as a "Presentation Layer."
    Do not just say "here is the data."
    Instead, you MUST summarize the data in a clear, natural language paragraph.
    Start with a heading, then present the key information from the data that directly answers the user's question.

    For example, if the user asked "Who are the top 5 highest paid employees?", you should respond like this:
    ## Top 5 Highest Paid Employees
    The top 5 highest paid employees are John Doe ($120,000), Jane Smith ($115,000), ...and so on.
    """
    messages = conversation_history + [vn.user_message(summary_prompt)]
    return vn.submit_prompt(messages)

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

    # Prepare conversation history for Vanna, keeping the last 10 messages for context
    conversation_for_vanna = [{"role": msg["role"], "content": msg["value"]} for msg in chat_history]
    if len(conversation_for_vanna) > 10:
        conversation_for_vanna = conversation_for_vanna[-10:]

    analytical_keywords = ["analyze", "analyse", "strategy", "improve", "loopholes", "recommend", "suggestions", "breakdown"]

    # Initialize response components
    sql = None
    df = None
    data_summary = ""
    strategic_analysis = ""
    error_message = None

    # --- Unified Brain Logic ---
    try:
        # STEP 1: Always attempt to answer the question directly with data (Brain #1)
        sql = vn.generate_sql(question=question, chat_history=conversation_for_vanna)

        if sql and is_sql_query(sql):
            try:
                df = vn.run_sql(sql)
                data_summary = summarize_data_with_llm(question, df, conversation_for_vanna)
            except Exception as e:
                # Critical Error Guardrail: If the database fails, stop immediately and report.
                error_response = f"Error: I could not execute the query. The database returned the following error:\n\n---\n{e}\n---"
                chat_history.append({"role": "assistant", "value": error_response, "sql": sql})
                with open(filepath, 'w') as f:
                    json.dump(chat_history, f, indent=2)
                return jsonify(chat_history)
        else:
            sql = None # Ensure sql is None if Vanna didn't generate a valid query

        # STEP 2: If strategic keywords are present, perform analysis (Brain #2)
        if any(keyword in question.lower() for keyword in analytical_keywords) and not error_message:
            if df is not None and not df.empty:
                # We have data, so analyze it directly
                synthesis_prompt = f"""
                The user's strategic question was: '{question}'.
                I have already retrieved the following data:
                {df.to_string()}
                Based ONLY on this data, provide a concise, strategic recommendation.
                Start with a summary, then a bulleted list of actionable insights.
                """
                strategic_analysis = vn.submit_prompt(conversation_for_vanna + [vn.user_message(synthesis_prompt)])
            else:
                # No direct data found, use the original sub-question method as a fallback
                deconstruct_prompt = f"""
                Break down this complex question into factual sub-questions I can answer with SQL: "{question}"
                Respond with ONLY a valid JSON object like: {{"sub_questions": ["question1", "question2", ...]}}
                """
                llm_response_str = vn.submit_prompt(conversation_for_vanna + [vn.user_message(deconstruct_prompt)])
                sub_questions_data = extract_json_from_response(llm_response_str)
                sub_questions = sub_questions_data.get("sub_questions", []) if sub_questions_data else []

                facts = []
                for sub_q in sub_questions:
                    sub_sql = vn.generate_sql(question=sub_q, chat_history=conversation_for_vanna)
                    if sub_sql and is_sql_query(sub_sql):
                        try:
                            sub_df = vn.run_sql(sub_sql)
                            facts.append(f"- For '{sub_q}', the data shows: {sub_df.to_string()}\\n")
                        except Exception as e:
                            facts.append(f"- When asking '{sub_q}', I got an error: {e}\\n")

                synthesis_prompt = f"""
                The user's question was: '{question}'.
                I gathered these facts:
                {''.join(facts)}
                Based ONLY on these facts, generate a concise strategic recommendation.
                """
                strategic_analysis = vn.submit_prompt(conversation_for_vanna + [vn.user_message(synthesis_prompt)])

        # STEP 3: Assemble the final response
        final_answer = ""
        if data_summary:
            final_answer += data_summary
        if strategic_analysis:
            if final_answer:
                final_answer += "\n\n---\n\n**Strategic Analysis:**\n"
            final_answer += strategic_analysis

        # STEP 4: Fallback if no answer was generated
        if not final_answer:
            if error_message:
                final_answer = error_message
            else:
                # If no SQL and no analysis, it's a general question for the base LLM
                final_answer = vn.submit_prompt(conversation_for_vanna)

        chat_history.append({"role": "assistant", "value": final_answer, "sql": sql})

    except Exception as e:
        # Broad exception handler for unexpected errors in the logic
        chat_history.append({"role": "assistant", "value": f"A critical error occurred: {e}", "sql": sql})

    # Save the updated conversation
    with open(filepath, 'w') as f:
        json.dump(chat_history, f, indent=2)

    return jsonify(chat_history)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
