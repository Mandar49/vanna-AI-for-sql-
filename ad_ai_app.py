# ad_ai_app.py
from flask import Flask, jsonify, request, render_template
import pandas as pd
import json
import re
import os

# Import the pre-trained Vanna instance from our common module
from common import vn

# Initialize the Flask application
app = Flask(__name__)

CONVERSATIONS_DIR = "conversations"
if not os.path.exists(CONVERSATIONS_DIR):
    os.makedirs(CONVERSATIONS_DIR)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/conversations', methods=['GET'])
def list_conversations():
    try:
        files = os.listdir(CONVERSATIONS_DIR)
        files.sort(key=lambda x: os.path.getmtime(os.path.join(CONVERSATIONS_DIR, x)), reverse=True)

        conversations = []
        for filename in files:
            if filename.endswith(".json"):
                with open(os.path.join(CONVERSATIONS_DIR, filename), 'r') as f:
                    data = json.load(f)
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
        return jsonify([])

def extract_json_from_response(response: str):
    match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        start = response.find('{')
        end = response.rfind('}') + 1
        if start != -1 and end != 0:
            try:
                return json.loads(response[start:end])
            except json.JSONDecodeError:
                return None
    return None

def summarize_data_with_llm(question: str, df: pd.DataFrame) -> str:
    if df.empty:
        return "I found no data for your question."

    if len(df) == 1 and len(df.columns) == 1:
        return f"The answer to your question '{question}' is: {df.iloc[0, 0]}"

    prompt = f"""
    The user asked: '{question}'.
    The retrieved data is:
    {df.to_string()}
    Summarize this data into a friendly, natural-language sentence.
    """
    return vn.submit_prompt([vn.user_message(prompt)])

def is_sql_query(s: str) -> bool:
    """
    A simple guardrail to check if a string looks like a SQL query.
    """
    s = s.strip().lower()
    return s.startswith("select") or s.startswith("with")

@app.route('/api/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question')
    conversation_id = data.get('conversation_id')

    if not all([question, conversation_id]):
        return jsonify({"error": "Question and conversation_id are required."}), 400

    filepath = os.path.join(CONVERSATIONS_DIR, f"{conversation_id}.json")

    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            chat_history = json.load(f)
    else:
        chat_history = []

    chat_history.append({"role": "user", "value": question})

    # Handle greetings and casual conversation
    greeting_keywords = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "greetings", "howdy"]
    question_lower = question.lower().strip()
    if any(question_lower == keyword or question_lower.startswith(keyword + " ") or question_lower.startswith(keyword + ",") for keyword in greeting_keywords):
        greeting_response = "Hello! I'm your AI assistant for analyzing business data. You can ask me questions about your data, or request strategic analysis. How can I help you today?"
        chat_history.append({"role": "assistant", "value": greeting_response, "sql": None})
        with open(filepath, 'w') as f:
            json.dump(chat_history, f, indent=2)
        return jsonify(chat_history)

    conversation_for_vanna = [{"role": msg["role"], "content": msg["value"]} for msg in chat_history]

    if len(conversation_for_vanna) > 4:
        conversation_for_vanna = conversation_for_vanna[-4:]

    analytical_keywords = ["analyze", "analyse", "strategy", "improve", "loopholes", "recommend", "suggestions", "breakdown"]

    if any(keyword in question.lower() for keyword in analytical_keywords):
        # --- Brain #2: The "Strategic Analyst Brain" ---
        try:
            deconstruct_prompt = f"""
            Break the strategic question "{question}" into 3-5 factual sub-questions.
            Respond with ONLY a valid JSON object in the format: {{"sub_questions": ["question1", "question2", ...]}}
            """
            llm_response_str = vn.submit_prompt([vn.user_message(deconstruct_prompt)])

            sub_questions = extract_json_from_response(llm_response_str).get("sub_questions", [])

            facts = []
            for sub_q in sub_questions:
                sql = vn.generate_sql(question=sub_q, chat_history=conversation_for_vanna)
                if sql and is_sql_query(sql):
                    try:
                        df = vn.run_sql(sql)
                        facts.append(f"- For '{sub_q}', data: {df.to_string()}\\n")
                    except Exception as e:
                        facts.append(f"- For '{sub_q}', error: {e}\\n")

            synthesis_prompt = f"""
            The user asked: '{question}'.
            Collected facts: {''.join(facts)}
            Based ONLY on these facts, provide a strategic recommendation.
            Format the response as a short summary paragraph followed by a clear, bulleted list of actionable recommendations.
            """
            final_answer = vn.submit_prompt([vn.user_message(synthesis_prompt)])

            chat_history.append({"role": "assistant", "value": final_answer, "sql": None})

        except Exception as e:
            chat_history.append({"role": "assistant", "value": f"An error occurred during strategic analysis: {e}", "sql": None})

    else:
        # --- Brain #1: The "Data Retrieval Brain" ---
        try:
            sql = vn.generate_sql(question=question, chat_history=conversation_for_vanna)

            # --- New Guardrail: SQL Validation ---
            if sql and is_sql_query(sql):
                df = vn.run_sql(sql)
                summary = summarize_data_with_llm(question, df)
                chat_history.append({"role": "assistant", "value": summary, "sql": sql})
            else:
                summary = "I could not generate a SQL query for your question. Please try rephrasing."
                chat_history.append({"role": "assistant", "value": summary, "sql": None})

        except Exception as e:
            chat_history.append({"role": "assistant", "value": f"An error occurred: {e}", "sql": None})

    with open(filepath, 'w') as f:
        json.dump(chat_history, f, indent=2)

    return jsonify(chat_history)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
