# ad_ai_app.py
from flask import Flask, jsonify, request, render_template
import pandas as pd
import json
import re
import os

# Import the pre-trained Vanna instance and utility functions
from common import vn
from utils import is_greeting, is_sql_query
from query_router import router
from sql_corrector import corrector
from business_analyst import analyst
from context_memory import memory
from response_composer import composer

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

@app.route('/api/clear_memory', methods=['POST'])
def clear_memory():
    """Clear conversation context memory"""
    try:
        memory.clear_memory()
        return jsonify({"success": True, "message": "Memory cleared successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/memory_stats', methods=['GET'])
def get_memory_stats():
    """Get memory statistics"""
    try:
        stats = memory.get_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

def summarize_data_with_llm(question: str, df: pd.DataFrame, sql: str = None) -> tuple:
    """
    Cognitive Fusion Layer - Uses Business Analyst + Response Composer
    Performs full data introspection with persona-based reasoning
    
    Returns:
        tuple: (response_text, persona_used, insights)
    """
    if df.empty:
        return ("I found no data for your question.", "analyst", None)

    # If the result is a single value, provide it with context
    if len(df) == 1 and len(df.columns) == 1:
        value = df.iloc[0, 0]
        response = f"📊 **Answer:** {value}\n\nThe answer to your question '{question}' is: {value}"
        return (response, "analyst", None)

    # Use Business Analyst for comprehensive data introspection
    analysis = analyst.analyze_results_with_llm(question, df, sql)
    
    # Add trend analysis
    trend = analyst.analyze_trends(df)
    if trend and "Insufficient" not in trend:
        analysis['trend'] = trend
    
    # Detect appropriate persona
    persona = composer.detect_persona(question)
    
    # Get recent context
    context = memory.recall_context(last_n=3)
    
    # Prepare raw data summary
    raw_data = df.head(10).to_string(index=False) if len(df) <= 10 else df.head(5).to_string(index=False)
    
    # Compose response with appropriate persona
    response = composer.compose_response(
        persona=persona,
        query=question,
        analysis=analysis,
        raw_data=raw_data,
        context=context
    )
    
    # Add trend if available
    if analysis.get('trend'):
        response += f"\n\n📈 **Trend:** {analysis['trend']}"
    
    return (response, persona, analysis.get('insight'))

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
                    # Use SQL corrector for error-tolerant execution
                    execution_result = corrector.execute_with_retry(sql, max_retries=1)
                    
                    if execution_result['success']:
                        df = execution_result['data']
                        facts.append(f"- For the question '{sub_q}', the data shows: {df.to_string()}\\n")
                    else:
                        facts.append(f"- When asking '{sub_q}', I encountered an error: {execution_result['message']}\\n")

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
        # --- Dual-Brain Routing System ---
        try:
            # Route the query to appropriate brain
            routing_result = router.route_query(question, chat_history)
            
            if routing_result["type"] == "sql":
                # --- SQL Brain (Vanna) ---
                sql = vn.generate_sql(question=question, chat_history=conversation_for_vanna)
                print(f"Generated SQL: {sql}")
                
                # --- Guardrail #2: SQL Validation & Auto-Correction ---
                if sql and is_sql_query(sql):
                    # Use SQL corrector for error-tolerant execution
                    execution_result = corrector.execute_with_retry(sql, max_retries=1)
                    
                    if execution_result['success']:
                        df = execution_result['data']
                        sql_used = execution_result['sql_used']
                        
                        # Log if correction was applied
                        if execution_result['correction_applied']:
                            print(f"✓ SQL auto-corrected:")
                            print(f"  Original: {execution_result['original_sql']}")
                            print(f"  Corrected: {sql_used}")
                        
                        # Cognitive Fusion Layer - Use Business Analyst + Response Composer
                        summary, persona, insights = summarize_data_with_llm(question, df, sql_used)
                        
                        # Add correction notice to response if applicable
                        if execution_result['correction_applied']:
                            summary = f"⚙️ {execution_result['message']}\n\n{summary}"
                        
                        # Store in context memory
                        memory.remember(
                            query=question,
                            response=summary,
                            sql=sql_used,
                            insights=insights,
                            persona=persona
                        )
                        
                        chat_history.append({"role": "assistant", "value": summary, "sql": sql_used})
                    else:
                        # SQL execution failed even after correction attempt
                        error_msg = execution_result['message']
                        if execution_result['correction_applied']:
                            error_msg += f"\n\nOriginal SQL: {execution_result['original_sql']}\nAttempted correction: {execution_result['sql_used']}"
                        
                        chat_history.append({"role": "assistant", "value": error_msg, "sql": sql})
                else:        
                    # If no valid SQL is generated, fall back to general brain
                    general_result = router._handle_general_query(question, chat_history)
                    chat_history.append({"role": "assistant", "value": general_result["answer"], "sql": None})
            
            elif routing_result["type"] == "general":
                # --- General Intelligence Brain (Mistral) ---
                answer = routing_result["answer"]
                chat_history.append({"role": "assistant", "value": answer, "sql": None})

        except Exception as e:
            error_msg = f"An error occurred while processing your question: {str(e)}"
            chat_history.append({"role": "assistant", "value": error_msg, "sql": None})

    # Save the updated conversation
    with open(filepath, 'w') as f:
        json.dump(chat_history, f, indent=2)

    return jsonify(chat_history)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
