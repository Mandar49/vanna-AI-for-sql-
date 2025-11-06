# ad_ai_app.py
from flask import Flask, jsonify, request, render_template
import json
import re
import os
import pandas as pd
from common import LocalVanna, run_sql

# Instantiate the Vanna class from the common module
vn = LocalVanna()

# Assign the shared database connection function
vn.run_sql = run_sql

# Initialize the Flask application
app = Flask(__name__)

CONVERSATIONS_DIR = "conversations"
if not os.path.exists(CONVERSATIONS_DIR):
    os.makedirs(CONVERSATIONS_DIR)

# Main route to serve the web frontend
@app.route('/')
def index():
    return render_template('index.html')

# API endpoint to get the list of conversations
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

# API endpoint to get a specific conversation
@app.route('/api/conversations/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    filepath = os.path.join(CONVERSATIONS_DIR, f"{conversation_id}.json")
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return jsonify(json.load(f))
    else:
        # If no conversation exists, send back an empty list
        return jsonify([])

# Robust JSON extraction from LLM response
def extract_json_from_response(response: str):
    match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
    if match:
        try: return json.loads(match.group(1))
        except json.JSONDecodeError: pass
    try: return json.loads(response)
    except json.JSONDecodeError:
        start = response.find('{'); end = response.rfind('}') + 1
        if start != -1 and end != 0:
            try: return json.loads(response[start:end])
            except json.JSONDecodeError: return None
    return None

def summarize_data(question: str, df: pd.DataFrame) -> str:
    if df.empty:
        return "I found no data for your question."
    if len(df) == 1 and len(df.columns) == 1:
         # For single-value results, format it nicely.
        return f"The answer to your question '{question}' is: {df.iloc[0, 0]}"

    prompt = f"""
    The user asked the following question: '{question}'.
    I ran a SQL query and got the following data in a pandas DataFrame:
    {df.to_string()}

    Summarize this data into a friendly, natural-language sentence that answers the user's question.
    Do not mention the DataFrame or SQL. Just provide a human-like answer.
    """
    return vn.submit_prompt([vn.user_message(prompt)])

@app.route('/api/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question')
    conversation_id = data.get('conversation_id')

    if not all([question, conversation_id]):
        return jsonify({"error": "Question and conversation_id are required."}), 400

    filepath = os.path.join(CONVERSATIONS_DIR, f"{conversation_id}.json")

    # Load history or create a new conversation
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            chat_history = json.load(f)
    else:
        chat_history = []

    chat_history.append({"role": "user", "value": question})

    # Extract the last 4 messages for conversational context
    # The Vanna `generate_sql` function expects a list of dictionaries with "role" and "content" keys
    # We also need to rename our "value" key to "content" to match the expected format
    conversation_for_vannna = [{"role": msg["role"], "content": msg["value"]} for msg in chat_history]

    # Keep the last 4 messages for context
    if len(conversation_for_vannna) > 4:
        conversation_for_vannna = conversation_for_vannna[-4:]

    analytical_keywords = ["analyze", "analyse", "strategy", "improve", "loopholes", "recommend"]

    if any(keyword in question.lower() for keyword in analytical_keywords):
        # --- "Strategic Analyst Brain" ---
        try:
            deconstruct_prompt = f"""
            Break the strategic question into 3-5 factual sub-questions.
            Respond with ONLY a valid JSON object in the format: {{"sub_questions": ["question1", "question2", ...]}}
            Strategic Question: "{question}"
            """
            llm_response_str = vn.submit_prompt([vn.user_message(deconstruct_prompt)])

            llm_response_json = extract_json_from_response(llm_response_str)
            sub_questions = llm_response_json.get("sub_questions", []) if llm_response_json else []

            facts = []
            for sub_q in sub_questions:
                sql = vn.generate_sql(question=sub_q, chat_history=conversation_for_vannna)
                if sql:
                    try:
                        df = vn.run_sql(sql)
                        facts.append(f"- For '{sub_q}', data: {df.to_string()}\\n")
                    except Exception as e:
                        facts.append(f"- For '{sub_q}', error: {e}\\n")

            synthesis_prompt = f"Original Question: '{question}'. Collected Facts: {''.join(facts)}. Based ONLY on these facts, provide a strategic recommendation."
            final_answer = vn.submit_prompt([vn.user_message(synthesis_prompt)])

            chat_history.append({"role": "assistant", "value": final_answer, "sql": None})

        except Exception as e:
            chat_history.append({"role": "assistant", "value": f"Error during strategic analysis: {e}", "sql": None})

    else:
        # --- "Data Retrieval Brain" ---
        try:
            sql = vn.generate_sql(question=question, chat_history=conversation_for_vannna)

            if sql:
                df = vn.run_sql(sql)
                summary = summarize_data(question, df)
                chat_history.append({"role": "assistant", "value": summary, "sql": sql})
            else:
                summary = "I could not generate a SQL query for your question. Please try rephrasing."
                chat_history.append({"role": "assistant", "value": summary, "sql": None})
        except Exception as e:
            chat_history.append({"role": "assistant", "value": f"An error occurred: {e}", "sql": None})

    # Save the updated conversation
    with open(filepath, 'w') as f:
        json.dump(chat_history, f, indent=2)

    return jsonify(chat_history)

# Main execution block
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
