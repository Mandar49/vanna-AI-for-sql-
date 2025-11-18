# ad_ai_app_hybrid.py - DB-INTELLIGENCE-V1 Main Application
# Hybrid AI Business Analyst combining SQL accuracy with business reasoning

from flask import Flask, jsonify, request, render_template, send_file
import pandas as pd
import json
import re
import os
from pathlib import Path
from datetime import datetime

# Import core components
from common import vn
from utils import is_greeting, is_sql_query
from query_router import router
from sql_corrector import corrector
from business_analyst import analyst
from context_memory import memory
from response_composer import composer
from data_validator import validator
from error_logger import error_logger
from export_manager import export_manager
from hybrid_reasoner import HybridReasoner
from profile_manager import (
    get_active_profile,
    set_active_profile,
    save_interaction,
    load_recent,
    list_profiles,
    init_profile,
    delete_profile,
    get_profile_stats
)

# Initialize Flask app
app = Flask(__name__)

# Register Dashboard Blueprint
from dashboard_gateway import dashboard_bp
app.register_blueprint(dashboard_bp)

# Initialize hybrid reasoner
hybrid_reasoner = HybridReasoner()

# Configuration
CONVERSATIONS_DIR = "conversations"
VANNA_TRAINING_FILE = "vanna_chroma_db/chroma.sqlite3"

if not os.path.exists(CONVERSATIONS_DIR):
    os.makedirs(CONVERSATIONS_DIR)

IS_TRAINED = os.path.exists(VANNA_TRAINING_FILE)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/ask', methods=['POST'])
def ask():
    """
    DB-INTELLIGENCE-V1: Hybrid query endpoint
    Combines SQL accuracy with business intelligence reasoning
    """
    if not IS_TRAINED:
        return jsonify([{
            "role": "assistant",
            "value": "Error: The AI model has not been trained. Please run `python train.py` from your terminal and then restart the application.",
            "sql": None
        }]), 200

    data = request.json
    question = data.get('question')
    conversation_id = data.get('conversation_id')
    profile_name = data.get('profile')
    
    # Get mode parameter
    mode = request.args.get('mode', data.get('mode', 'detailed')).upper()
    if mode not in ['COMPACT', 'DETAILED']:
        mode = 'DETAILED'
    
    composer.set_mode(mode)

    if not all([question, conversation_id]):
        return jsonify({"error": "Question and conversation_id are required."}), 400
    
    current_profile = profile_name or get_active_profile()
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

    # Handle greetings
    if is_greeting(question):
        greeting_msg = "Hello! I'm DB-INTELLIGENCE-V1, your hybrid AI Business Analyst. I combine strict SQL accuracy with advanced business intelligence. Ask me about your data, business concepts, or strategic recommendations."
        chat_history.append({
            "role": "assistant",
            "value": greeting_msg,
            "sql": None
        })
        with open(filepath, 'w') as f:
            json.dump(chat_history, f, indent=2)
        return jsonify(chat_history)

    # Prepare conversation context
    conversation_for_vanna = [{"role": msg["role"], "content": msg["value"]} for msg in chat_history]
    if len(conversation_for_vanna) > 4:
        conversation_for_vanna = conversation_for_vanna[-4:]

    try:
        # Route query using hybrid intelligence
        routing_result = router.route_query(question, chat_history)
        
        if routing_result["type"] == "general":
            # General knowledge question - no SQL needed
            answer = routing_result["answer"]
            formatted_response = composer.compose_general_answer(answer)
            
            chat_history.append({
                "role": "assistant",
                "value": formatted_response,
                "sql": None
            })
            
        elif routing_result["type"] == "person":
            # Person query - search database first
            response_msg = handle_person_query(question)
            chat_history.append({
                "role": "assistant",
                "value": response_msg,
                "sql": None
            })
            
        elif routing_result["type"] == "sql":
            # SQL query - execute and apply hybrid reasoning
            response_msg, sql_used = handle_sql_query(question, conversation_for_vanna, mode, current_profile)
            chat_history.append({
                "role": "assistant",
                "value": response_msg,
                "sql": sql_used
            })
        
        # Save conversation
        with open(filepath, 'w') as f:
            json.dump(chat_history, f, indent=2)
        
        return jsonify(chat_history)
        
    except Exception as e:
        error_msg = f"Error processing query: {str(e)}"
        print(f"[ERROR] {error_msg}")
        import traceback
        traceback.print_exc()
        
        chat_history.append({
            "role": "assistant",
            "value": error_msg,
            "sql": None
        })
        
        with open(filepath, 'w') as f:
            json.dump(chat_history, f, indent=2)
        
        return jsonify(chat_history)


def handle_person_query(question: str) -> str:
    """Handle person-specific queries"""
    import re
    
    name_match = re.search(r'(?:about|is|named)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', question)
    
    if name_match:
        person_name = name_match.group(1)
        person_result = analyst.check_person_in_database(person_name)
        
        separator = "─" * 60
        
        if person_result['found']:
            data = person_result['data']
            table = person_result['table']
            
            response_msg = f"{separator}\nSQL RESULT\n{separator}\n"
            response_msg += f"Person found in {table} table:\n\n"
            
            for key, value in data.items():
                response_msg += f"{key}: {value}\n"
            
            response_msg += f"\n{separator}\nINSIGHT\n{separator}\n"
            response_msg += f"{person_name} exists in your database. All information shown above is from the {table} table."
            
            return response_msg
        else:
            response_msg = f"{separator}\nSQL RESULT\n{separator}\n"
            response_msg += "No data found matching the query criteria.\n\n"
            response_msg += f"{separator}\nINSIGHT\n{separator}\n"
            response_msg += f"{person_name} does not exist in your database. This person is not in the employees or customers tables."
            response_msg += f"\n\n{separator}\nSTRATEGIC RECOMMENDATION\n{separator}\n"
            response_msg += "Verify the name spelling or add this person to the database if they should be tracked."
            
            return response_msg
    else:
        return "Could not extract person name from query. Please specify the full name."


def handle_sql_query(question: str, conversation_history: list, mode: str, profile: str) -> tuple:
    """
    Handle SQL queries with hybrid intelligence
    Returns: (response_message, sql_used)
    """
    # Generate SQL
    sql = vn.generate_sql(question=question, chat_history=conversation_history)
    print(f"[SQL GENERATED] {sql}")
    
    if not sql or not is_sql_query(sql):
        return ("Could not generate valid SQL for this question.", None)
    
    # Execute SQL with retry
    execution_result = corrector.execute_with_retry(sql, max_retries=1)
    
    if execution_result['success']:
        df = execution_result['data']
        sql_used = execution_result['sql_used']
        
        if execution_result['correction_applied']:
            print(f"[SQL CORRECTED] {sql_used}")
        
        # Apply hybrid intelligence analysis
        hybrid_analysis = analyst.analyze_with_hybrid_intelligence(question, df, sql_used)
        
        # Format response using composer
        response_msg = composer.compose_hybrid_response(
            sql_result=hybrid_analysis['sql_result'],
            insight=hybrid_analysis['insight'],
            recommendation=hybrid_analysis['recommendation'],
            sql_query=sql_used if mode == 'DETAILED' else None,
            mode=mode
        )
        
        # Add correction notice if applicable
        if execution_result['correction_applied']:
            response_msg = f"⚙️ {execution_result['message']}\n\n{response_msg}"
        
        # Store in memory
        memory.remember(
            query=question,
            response=response_msg,
            sql=sql_used,
            insights=hybrid_analysis['insight'],
            persona='hybrid'
        )
        
        # Store in profile
        if profile:
            save_interaction(
                profile=profile,
                query=question,
                response=response_msg,
                sql=sql_used,
                metadata={
                    "framework": hybrid_analysis.get('framework_used'),
                    "mode": mode
                }
            )
        
        return (response_msg, sql_used)
        
    else:
        # SQL execution failed
        error_message = execution_result.get('message', 'Unknown error')
        reason = execution_result.get('reason', error_message)
        suggestion = execution_result.get('suggestion', 'Try rephrasing your question')
        
        # Log error
        error_logger.log_sql_error(
            error_type="EXECUTION_ERROR",
            sql=execution_result.get('sql_used', sql),
            error_message=error_message,
            question=question,
            context={"mode": mode, "profile": profile}
        )
        
        # Format error response with hybrid reasoning
        separator = "─" * 60
        error_msg = f"{separator}\nSQL RESULT\n{separator}\n"
        error_msg += f"Query execution failed.\n\n"
        error_msg += f"{separator}\nINSIGHT\n{separator}\n"
        error_msg += f"Reason: {reason}\n\n"
        error_msg += f"{separator}\nSTRATEGIC RECOMMENDATION\n{separator}\n"
        error_msg += f"{suggestion}"
        
        if mode == 'DETAILED':
            error_msg += f"\n\n{separator}\nSQL QUERY ATTEMPTED\n{separator}\n{sql}"
        
        return (error_msg, sql)


# Keep all other endpoints from original ad_ai_app.py
# (conversations, memory, exports, etc.)

if __name__ == '__main__':
    print("=" * 60)
    print("DB-INTELLIGENCE-V1: Hybrid AI Business Analyst")
    print("=" * 60)
    print("✓ SQL Accuracy: Strict data validation")
    print("✓ Business Intelligence: Advanced reasoning frameworks")
    print("✓ General Knowledge: Concept explanations")
    print("✓ Context Memory: Conversation-aware")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
