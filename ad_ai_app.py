# ad_ai_app.py
from flask import Flask, jsonify, request, render_template
import pandas as pd
import json
import re
import os
from pathlib import Path
from datetime import datetime

# Import the pre-trained Vanna instance and utility functions
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

# Initialize the Flask application
app = Flask(__name__)

# Register Dashboard Blueprint
from dashboard_gateway import dashboard_bp
app.register_blueprint(dashboard_bp)

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

@app.route('/api/error_logs', methods=['GET'])
def get_error_logs():
    """Get recent error logs"""
    try:
        n = request.args.get('n', default=10, type=int)
        errors = error_logger.get_recent_errors(n=n)
        return jsonify({"errors": errors, "count": len(errors)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/error_logs', methods=['DELETE'])
def clear_error_logs():
    """Clear error logs"""
    try:
        error_logger.clear_log()
        return jsonify({"success": True, "message": "Error logs cleared"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/clear_cache', methods=['POST'])
def clear_cache():
    """Clear query cache"""
    try:
        from query_cache import query_cache
        query_cache.clear_cache()
        return jsonify({"success": True, "message": "Query cache cleared"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/refresh_schema', methods=['POST'])
def refresh_schema_endpoint():
    """Refresh database schema by re-reading tables"""
    try:
        import mysql.connector
        
        # Database connection info
        db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'root',
            'database': 'ad_ai_testdb'
        }
        
        # Connect to database
        conn = mysql.connector.connect(**db_config)
        cursor = cursor()
        
        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        table_count = len(tables)
        
        # Get table schemas
        schema_info = []
        for (table_name,) in tables:
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            schema_info.append({
                'table': table_name,
                'columns': [col[0] for col in columns]
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Schema refreshed successfully. Found {table_count} tables.',
            'table_count': table_count,
            'tables': [s['table'] for s in schema_info],
            'database': db_config['database']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to refresh schema: {str(e)}'
        }), 500

@app.route('/api/export_report', methods=['POST'])
def export_report():
    """Export query results to CSV or PDF"""
    try:
        from export_manager import export_manager
        from flask import send_file
        
        data = request.json
        export_format = data.get('format', 'csv').lower()
        question = data.get('question', 'Query')
        sql = data.get('sql', '')
        results = data.get('results', [])
        summary = data.get('summary', '')
        dark_mode = data.get('dark_mode', False)
        
        print(f"[EXPORT] Format: {export_format}, Question: {question}")
        print(f"[EXPORT] SQL: {sql[:100] if sql else 'None'}...")
        print(f"[EXPORT] Results provided: {len(results) if results else 0} rows")
        print(f"[EXPORT] Summary length: {len(summary) if summary else 0} chars")
        
        # Convert results to DataFrame or use last saved result
        df = None
        use_last_result = False
        
        if results and len(results) > 0:
            df = pd.DataFrame(results)
            print(f"[EXPORT] Created DataFrame: {len(df)} rows x {len(df.columns)} columns")
        else:
            # No results provided - use last saved result
            use_last_result = True
            print("[EXPORT] No results in request, will use last saved query result")
        
        # Export based on format
        if export_format == 'csv':
            result = export_manager.export_to_csv(question, sql, df, summary, use_last_result)
        elif export_format == 'pdf':
            result = export_manager.export_to_pdf(question, sql, df, summary, dark_mode, use_last_result)
        else:
            return jsonify({
                'success': False,
                'message': f'Unsupported format: {export_format}'
            }), 400
        
        if result['success']:
            print(f"[EXPORT] Success: {result['filename']}")
            # Return file for download
            return send_file(
                result['filepath'],
                as_attachment=True,
                download_name=result['filename'],
                mimetype='text/csv' if export_format == 'csv' else 'application/pdf'
            )
        else:
            print(f"[EXPORT] Failed: {result['message']}")
            return jsonify(result), 400
    
    except Exception as e:
        error_msg = f'Export failed: {str(e)}'
        print(f"[EXPORT ERROR] {error_msg}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': error_msg
        }), 500

@app.route('/api/forecast', methods=['POST'])
def calculate_forecast():
    """
    Calculate CAGR and forecast for specified years
    
    Request body:
    {
        "start_year": 2023,
        "end_year": 2024,
        "forecast_years": [2025, 2026]
    }
    """
    try:
        data = request.json
        start_year = data.get('start_year')
        end_year = data.get('end_year')
        forecast_years = data.get('forecast_years', [])
        
        if not start_year or not end_year:
            return jsonify({"error": "start_year and end_year are required"}), 400
        
        # Calculate CAGR and forecasts
        result = corrector.calculate_cagr_sql(start_year, end_year, forecast_years)
        
        if not result['success']:
            return jsonify({
                "success": False,
                "message": result['message']
            }), 400
        
        # Validate CAGR
        is_valid, validation_msg = validator.validate_cagr(
            result['cagr'],
            result['start_sales'],
            result['end_sales'],
            start_year,
            end_year
        )
        
        # Validate forecasts
        forecast_validations = {}
        if forecast_years:
            for year in forecast_years:
                years_ahead = year - end_year
                if year in result['forecast']:
                    is_valid_forecast, forecast_msg = validator.validate_forecast(
                        result['forecast'][year],
                        result['end_sales'],
                        result['cagr_decimal'],
                        years_ahead
                    )
                    forecast_validations[year] = {
                        'valid': is_valid_forecast,
                        'message': forecast_msg
                    }
        
        return jsonify({
            "success": True,
            "cagr": result['cagr'],
            "start_year": start_year,
            "end_year": end_year,
            "start_sales": result['start_sales'],
            "end_sales": result['end_sales'],
            "forecast": result['forecast'],
            "scenarios": result['scenarios'],
            "validation": {
                "cagr_valid": is_valid,
                "cagr_message": validation_msg,
                "forecast_validations": forecast_validations
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Profile Management Endpoints ---

@app.route('/api/profiles', methods=['GET'])
def get_profiles():
    """List all available profiles"""
    try:
        profiles = list_profiles()
        active = get_active_profile()
        return jsonify({
            "profiles": profiles,
            "active_profile": active
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/profiles', methods=['POST'])
def create_profile():
    """Create a new profile"""
    try:
        data = request.json
        name = data.get('name')
        persona = data.get('persona', 'Analyst')
        
        if not name:
            return jsonify({"error": "Profile name is required"}), 400
        
        metadata = init_profile(name, persona=persona)
        return jsonify({
            "success": True,
            "profile": metadata
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/profiles/<profile_name>', methods=['DELETE'])
def remove_profile(profile_name):
    """Delete a profile"""
    try:
        success = delete_profile(profile_name)
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/profiles/<profile_name>/activate', methods=['POST'])
def activate_profile(profile_name):
    """Set active profile"""
    try:
        success = set_active_profile(profile_name)
        return jsonify({
            "success": success,
            "active_profile": get_active_profile()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/profiles/<profile_name>/stats', methods=['GET'])
def profile_stats(profile_name):
    """Get profile statistics"""
    try:
        stats = get_profile_stats(profile_name)
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/profiles/<profile_name>/history', methods=['GET'])
def profile_history(profile_name):
    """Get profile interaction history"""
    try:
        n = request.args.get('n', default=10, type=int)
        history = load_recent(profile_name, n=n)
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Orchestration Endpoints ---

@app.route('/api/command', methods=['POST'])
def execute_orchestrator_command():
    """Execute orchestrator command"""
    try:
        from orchestrator import execute_command
        
        data = request.json
        command = data.get('command')
        profile = data.get('profile')
        
        if not command:
            return jsonify({"error": "Command is required"}), 400
        
        result = execute_command(command, profile=profile)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/orchestration/history', methods=['GET'])
def get_orchestration_history_endpoint():
    """Get orchestration history"""
    try:
        from orchestrator import get_orchestration_history
        
        limit = request.args.get('limit', default=50, type=int)
        history = get_orchestration_history(limit=limit)
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Authentication Endpoints ---

def _log_auth_attempt(username: str, success: bool, ip: str = None):
    """Log authentication attempts to auth.log"""
    try:
        log_dir = "reports/logs"
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        log_file = os.path.join(log_dir, "auth.log")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "SUCCESS" if success else "FAILED"
        ip_info = f" from {ip}" if ip else ""
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {status}: User '{username}' login attempt{ip_info}\n")
    except Exception as e:
        print(f"Warning: Could not write to auth.log: {e}")

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        from auth_manager import register_user
        
        data = request.json
        username = data.get('username')
        password = data.get('password')
        role = data.get('role', 'analyst')
        
        result = register_user(username, password, role)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def api_login():
    """Authenticate user and create session - JSON API"""
    try:
        from auth_manager import authenticate_user
        
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            _log_auth_attempt(username or "unknown", False, request.remote_addr)
            return jsonify({
                "success": False,
                "message": "Username and password are required"
            }), 400
        
        result = authenticate_user(username, password)
        
        # Log the attempt
        _log_auth_attempt(username, result.get("success", False), request.remote_addr)
        
        if result.get("success"):
            return jsonify(result), 200
        else:
            return jsonify(result), 401
            
    except Exception as e:
        _log_auth_attempt("unknown", False, request.remote_addr)
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    """Authenticate user - JSON response (alternative endpoint)"""
    try:
        from auth_manager import authenticate_user
        
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            _log_auth_attempt(username or "unknown", False, request.remote_addr)
            return jsonify({
                "success": False,
                "message": "Username and password are required"
            }), 400
        
        result = authenticate_user(username, password)
        
        # Log the attempt
        _log_auth_attempt(username, result.get("success", False), request.remote_addr)
        
        if result.get("success"):
            return jsonify(result), 200
        else:
            return jsonify(result), 401
            
    except Exception as e:
        _log_auth_attempt("unknown", False, request.remote_addr)
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout user"""
    try:
        from auth_manager import logout_user
        
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        success = logout_user(token)
        
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    """List all users (admin only)"""
    try:
        from auth_manager import list_users, get_current_user
        
        # Check authentication
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user = get_current_user(token)
        
        if not user or user['role'] != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        
        users = list_users()
        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/me', methods=['GET'])
def get_current_user_endpoint():
    """Get current authenticated user"""
    try:
        from auth_manager import get_current_user
        
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user = get_current_user(token)
        
        if not user:
            return jsonify({"error": "Not authenticated"}), 401
        
        return jsonify(user)
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

def summarize_data_with_llm(question: str, df: pd.DataFrame, sql: str = None, mode: str = "DETAILED") -> tuple:
    """
    Cognitive Fusion Layer - Uses Business Analyst + Response Composer
    Performs full data introspection with persona-based reasoning
    
    STRICT MODE: Always show raw SQL results first, then analysis
    
    Args:
        question: User's question
        df: DataFrame with query results
        sql: SQL query executed
        mode: COMPACT or DETAILED response mode
    
    Returns:
        tuple: (response_text, persona_used, insights)
    """
    if df.empty:
        return ("No data available for this query in the current database.\n\nPlease populate the database with sample salesorders and orderitems.", "analyst", None)

    # ALWAYS show raw SQL results first (plain text format)
    response_parts = []
    separator = "─" * 60
    response_parts.append(separator)
    response_parts.append("SQL RESULT")
    response_parts.append(separator)
    
    # Format the raw data clearly
    if mode == "COMPACT" and len(df) > 5:
        response_parts.append(df.head(5).to_string(index=False))
        response_parts.append(f"\n... ({len(df) - 5} more rows)")
    elif len(df) <= 20:
        response_parts.append(df.to_string(index=False))
    else:
        response_parts.append(df.head(10).to_string(index=False))
        response_parts.append(f"\n... ({len(df) - 10} more rows)")
    
    response_parts.append(separator)
    
    # Check if this is a CAGR or forecast query
    is_cagr_query = analyst.detect_cagr_query(question)
    is_forecast_query = analyst.detect_forecast_query(question)
    
    if is_cagr_query or is_forecast_query:
        start_year, end_year = analyst.extract_years_from_query(question)
        
        if start_year and end_year:
            # Extract forecast years if this is a forecast query
            forecast_years = []
            if is_forecast_query:
                forecast_years = analyst.extract_forecast_years(question)
            
            # Calculate CAGR and forecasts directly from SQL
            cagr_result = corrector.calculate_cagr_sql(start_year, end_year, forecast_years)
            
            if cagr_result['success']:
                # Add CAGR to SQL results (plain text)
                response_parts.append(f"\nCAGR (Direct from Database): {cagr_result['cagr']}%")
                response_parts.append(f"Period: {start_year} to {end_year}")
                if mode == "DETAILED":
                    response_parts.append(f"Starting Sales: {cagr_result['start_sales']:.2f}")
                    response_parts.append(f"Ending Sales: {cagr_result['end_sales']:.2f}")
                
                # Add forecast summary if available
                if cagr_result.get('forecast'):
                    response_parts.append(f"\nForecasts Generated: {', '.join(map(str, sorted(cagr_result['forecast'].keys())))}")
                
                # Validate CAGR
                is_valid, validation_msg = validator.validate_cagr(
                    cagr_result['cagr'],
                    cagr_result['start_sales'],
                    cagr_result['end_sales'],
                    start_year,
                    end_year
                )
                print(f"[VALIDATION] {validation_msg}")
                
                # Use CAGR-specific analysis
                analysis = analyst.analyze_with_cagr(question, df, cagr_result)
                
                # Compose CAGR response (includes forecast section if available)
                raw_data = df.head(10).to_string(index=False) if len(df) <= 10 else df.head(5).to_string(index=False)
                analysis_response = composer.compose_cagr_response(analysis, raw_data, df, mode)
                
                response_parts.append("\n" + analysis_response)
                
                return ("\n".join(response_parts), "analyst", analysis.get('insight'))
    
    # If the result is a single value, provide it prominently
    if len(df) == 1 and len(df.columns) == 1:
        value = df.iloc[0, 0]
        response_parts.append(f"\nDirect Answer: {value}")
        return ("\n".join(response_parts), "analyst", None)

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
    
    # Prepare raw data summary for LLM
    raw_data = df.head(10).to_string(index=False) if len(df) <= 10 else df.head(5).to_string(index=False)
    
    # Compose response with appropriate persona
    analysis_response = composer.compose_response(
        persona=persona,
        query=question,
        analysis=analysis,
        raw_data=raw_data,
        context=context,
        df=df,
        mode=mode
    )
    
    # Add analysis section
    response_parts.append("\n" + analysis_response)
    
    # Note: Trend is already included in analysis_response from compose_response()
    # No need to add it again here to avoid duplication
    
    # Add data verification note
    response_parts.append("\n\nNote: All numbers above are from the actual database query results.")
    
    return ("\n".join(response_parts), persona, analysis.get('insight'))

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
    profile_name = data.get('profile')  # Optional profile parameter
    
    # Get mode parameter from query string or request body
    mode = request.args.get('mode', data.get('mode', 'detailed')).upper()
    if mode not in ['COMPACT', 'DETAILED']:
        mode = 'DETAILED'
    
    # Set composer mode
    composer.set_mode(mode)

    if not all([question, conversation_id]):
        return jsonify({"error": "Question and conversation_id are required."}), 400
    
    # Use specified profile or active profile
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
                        
                        # Check if query returned empty results
                        if df.empty:
                            # Log empty result
                            error_logger.log_sql_error(
                                error_type="EMPTY_RESULT",
                                sql=sql_used,
                                error_message="Query executed successfully but returned no data",
                                question=question,
                                context={"mode": mode, "profile": current_profile}
                            )
                            
                            # Graceful user-friendly message (plain text)
                            separator = "─" * 60
                            empty_msg = f"{separator}\n"
                            empty_msg += "NO DATA FOUND\n"
                            empty_msg += f"{separator}\n\n"
                            empty_msg += "No data found for this query.\n\n"
                            empty_msg += "Possible causes:\n"
                            empty_msg += "- No data exists for the given year or time period\n"
                            empty_msg += "- Filters are too narrow or restrictive\n"
                            empty_msg += "- The database tables may need to be populated\n\n"
                            empty_msg += f"SQL Query:\n{sql_used}\n\n"
                            empty_msg += "Suggestion: Try 'Show me all customers' or 'List all orders' to verify data exists."
                            
                            chat_history.append({"role": "assistant", "value": empty_msg, "sql": sql_used})
                        else:
                            # Cognitive Fusion Layer - Use Business Analyst + Response Composer
                            summary, persona, insights = summarize_data_with_llm(question, df, sql_used, mode)
                            
                            # Validate that response doesn't contain fabricated numbers
                            is_valid, suspicious_numbers = validator.validate_response(summary, df)
                            if not is_valid:
                                print(f"⚠️ Warning: Suspicious numbers detected in response: {suspicious_numbers}")
                                summary = validator.add_validation_warning(summary, suspicious_numbers)
                            
                            # Add correction notice to response if applicable
                            if execution_result['correction_applied']:
                                summary = f"⚙️ {execution_result['message']}\n\n{summary}"
                            
                            # Add SQL query used for transparency (plain text format)
                            separator = "─" * 60
                            summary += f"\n\n{separator}\nSQL QUERY\n{separator}\n{sql_used}"
                            
                            # Store in context memory
                            memory.remember(
                                query=question,
                                response=summary,
                                sql=sql_used,
                                insights=insights,
                                persona=persona
                            )
                            
                            # Store in profile context if profile is active
                            if current_profile:
                                save_interaction(
                                    profile=current_profile,
                                    query=question,
                                    response=summary,
                                    sql=sql_used,
                                    metadata={
                                        "persona": persona,
                                        "insights": insights
                                    }
                                )
                            
                            chat_history.append({"role": "assistant", "value": summary, "sql": sql_used})
                    else:
                        # SQL execution failed even after correction attempt
                        error_message = execution_result['message']
                        
                        # Determine error type
                        if "1064" in error_message or "syntax" in error_message.lower():
                            error_type = "SYNTAX_ERROR"
                            user_message = "Invalid SQL syntax. Please adjust your query or check table names."
                        elif "1146" in error_message or "doesn't exist" in error_message.lower():
                            error_type = "TABLE_NOT_FOUND"
                            user_message = "Table or column not found. Please check the database schema."
                        elif "1054" in error_message or "unknown column" in error_message.lower():
                            error_type = "COLUMN_NOT_FOUND"
                            user_message = "Column not found. Please verify column names in the database."
                        else:
                            error_type = "EXECUTION_ERROR"
                            user_message = "SQL execution failed. Please try rephrasing your question."
                        
                        # Log the error
                        error_logger.log_sql_error(
                            error_type=error_type,
                            sql=execution_result.get('sql_used', sql),
                            error_message=error_message,
                            question=question,
                            context={
                                "mode": mode,
                                "profile": current_profile,
                                "correction_applied": execution_result.get('correction_applied', False),
                                "original_sql": execution_result.get('original_sql', sql)
                            }
                        )
                        
                        # Graceful user-friendly message (plain text)
                        separator = "─" * 60
                        error_msg = f"{separator}\n"
                        error_msg += "SQL ERROR\n"
                        error_msg += f"{separator}\n\n"
                        error_msg += f"{user_message}\n\n"
                        
                        if mode == "DETAILED":
                            error_msg += f"Technical Details:\n{error_message}\n\n"
                            
                            if execution_result.get('correction_applied'):
                                error_msg += f"Original SQL:\n{execution_result['original_sql']}\n\n"
                                error_msg += f"Attempted Correction:\n{execution_result['sql_used']}\n\n"
                            else:
                                error_msg += f"SQL Query:\n{sql}\n\n"
                        
                        error_msg += "Suggestion: Try rephrasing your question or ask 'What tables are available?'"
                        
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
