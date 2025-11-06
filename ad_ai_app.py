# ad_ai_app.py
from flask import Flask, jsonify, request, render_template
import pandas as pd
import json
import re
from datetime import datetime

# Import the pre-trained Vanna instance from our common module
from common import vn

# Initialize the Flask application
app = Flask(__name__)

# In-memory storage for conversations
conversations = {}

def extract_json_from_response(response: str):
    """
    A helper function to robustly extract a JSON object from a string,
    even if it's embedded within Markdown code blocks.
    """
    # First, try to find a JSON blob within ```json ... ```
    match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass  # Fall through to the next method if parsing fails

    # If not found or if parsing failed, try to load the whole string as JSON
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        # If that fails, find the first '{' and last '}' and try to parse that substring
        start = response.find('{')
        end = response.rfind('}') + 1
        if start != -1 and end != 0:
            try:
                return json.loads(response[start:end])
            except json.JSONDecodeError:
                return None  # Return None if all attempts fail
    return None

@app.route('/')
def index():
    """
    Serve the main chat interface.
    """
    return render_template('index.html')

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    """
    Return a list of all conversations with their titles.
    """
    conv_list = []
    for conv_id, conv_data in conversations.items():
        title = conv_data.get('title', 'New Chat')
        conv_list.append({'id': conv_id, 'title': title})
    return jsonify(conv_list)

@app.route('/api/conversations/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """
    Return the full history of a specific conversation.
    """
    if conversation_id in conversations:
        return jsonify(conversations[conversation_id]['history'])
    return jsonify([])

def summarize_data_with_llm(question: str, df: pd.DataFrame) -> str:
    """
    The 'Presentation Layer'. Takes a user's question and a pandas DataFrame,
    and uses the LLM to generate a friendly, natural-language summary of the data.
    """
    if df.empty:
        return "I found no data for your question."

    # For single-value results, we can format it nicely without calling the LLM.
    if len(df) == 1 and len(df.columns) == 1:
        return f"The answer to your question '{question}' is: {df.iloc[0, 0]}"

    # Convert the DataFrame to a string format for the prompt
    df_str = df.to_string()

    prompt = f"""
    The user asked the following question: '{question}'.
    I have retrieved the following data from the database:
    {df_str}

    Please summarize this data into a friendly, natural-language sentence that directly answers the user's question.
    Do not mention the DataFrame, SQL, or the database. Just provide a human-like answer.
    """

    # Use the Vanna instance (which has the LLM connection) to submit the prompt
    return vn.submit_prompt([vn.user_message(prompt)])

@app.route('/api/ask', methods=['POST'])
def ask():
    """
    The main API endpoint that powers the application.
    It implements the "Two-Brain" logic to handle different types of questions.
    """
    data = request.json
    question = data.get('question')
    conversation_id = data.get('conversation_id')

    if not question:
        return jsonify({"error": "A 'question' is required."}), 400
    
    # Initialize conversation if it doesn't exist
    if conversation_id not in conversations:
        conversations[conversation_id] = {
            'title': question[:50],  # Use first 50 chars of first question as title
            'history': []
        }
    
    # Add user message to history
    conversations[conversation_id]['history'].append({
        'role': 'user',
        'value': question
    })

    # --- Two-Brain System Logic ---
    
    # Handle greetings and casual conversation
    greeting_keywords = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "greetings"]
    if any(question.lower().strip() == keyword or question.lower().strip().startswith(keyword + " ") for keyword in greeting_keywords):
        greeting_response = "Hello! I'm your AI assistant for analyzing advertising data. You can ask me questions about your data, or request strategic analysis. How can I help you today?"
        conversations[conversation_id]['history'].append({
            'role': 'assistant',
            'value': greeting_response,
            'sql': None
        })
        return jsonify(conversations[conversation_id]['history'])
    
    analytical_keywords = ["analyze", "analyse", "strategy", "improve", "loopholes", "recommend"]

    if any(keyword in question.lower() for keyword in analytical_keywords):
        # --- Brain #2: The "Strategic Analyst Brain" ---
        try:
            # 1. Deconstruct: Break the complex question into sub-questions
            deconstruct_prompt = f"""
            The user has a complex strategic question. Your task is to break it down into 3-5 smaller, factual sub-questions that can be answered with a SQL query.
            Respond with ONLY a valid JSON object in the format: {{"sub_questions": ["question1", "question2", ...]}}

            Here is the user's strategic question: "{question}"
            """
            llm_response_str = vn.submit_prompt([vn.user_message(deconstruct_prompt)])

            llm_response_json = extract_json_from_response(llm_response_str)
            sub_questions = llm_response_json.get("sub_questions", []) if llm_response_json else []

            # 2. Delegate & Gather Facts: Use Vanna to answer each sub-question
            facts = []
            for sub_q in sub_questions:
                sql = vn.generate_sql(question=sub_q)
                if sql:
                    try:
                        df = vn.run_sql(sql)
                        facts.append(f"- For the question '{sub_q}', the data is: {df.to_string()}\\n")
                    except Exception as e:
                        facts.append(f"- When trying to answer '{sub_q}', I encountered an error: {e}\\n")

            # 3. Synthesize & Reason: Combine the facts into a final strategic recommendation
            synthesis_prompt = f"""
            You are a strategic business analyst. The user asked the following high-level question: '{question}'.
            I have gathered the following facts by querying our database:
            {''.join(facts)}

            Based ONLY on these facts, please provide a comprehensive, human-like strategic recommendation.
            Do not mention the sub-questions or the data gathering process. Just provide the final analysis.
            """
            final_answer = vn.submit_prompt([vn.user_message(synthesis_prompt)])

            # Add AI response to history
            conversations[conversation_id]['history'].append({
                'role': 'assistant',
                'value': final_answer,
                'sql': None
            })
            
            return jsonify(conversations[conversation_id]['history'])

        except Exception as e:
            error_msg = f"An error occurred during strategic analysis: {e}"
            conversations[conversation_id]['history'].append({
                'role': 'assistant',
                'value': error_msg,
                'sql': None
            })
            return jsonify(conversations[conversation_id]['history'])

    else:
        # --- Brain #1: The "Data Retrieval Brain" ---
        try:
            # Use Vanna's core RAG workflow to generate SQL and get data
            sql = vn.generate_sql(question=question)

            if sql:
                df = vn.run_sql(sql)
                # Use the presentation layer to summarize the data
                summary = summarize_data_with_llm(question, df)
                
                # Add AI response to history
                conversations[conversation_id]['history'].append({
                    'role': 'assistant',
                    'value': summary,
                    'sql': sql
                })
                
                return jsonify(conversations[conversation_id]['history'])
            else:
                summary = "I could not generate a SQL query for your question. Please try rephrasing."
                
                conversations[conversation_id]['history'].append({
                    'role': 'assistant',
                    'value': summary,
                    'sql': None
                })
                
                return jsonify(conversations[conversation_id]['history'])

        except Exception as e:
            error_msg = f"An error occurred: {e}"
            conversations[conversation_id]['history'].append({
                'role': 'assistant',
                'value': error_msg,
                'sql': None
            })
            return jsonify(conversations[conversation_id]['history'])

# Main execution block
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
