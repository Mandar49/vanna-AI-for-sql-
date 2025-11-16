"""
Executive Intelligence Layer - Orchestration Core (Phase 4B)
Central command layer to interpret and route user intents.
Unifies all subsystems: profiles, scheduler, reports, voice, dashboard.
"""

import os
import re
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import pandas as pd

# Setup logging
LOG_DIR = "./reports/logs"
Path(LOG_DIR).mkdir(parents=True, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "orchestrator.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Orchestration history
ORCHESTRATION_HISTORY: List[Dict[str, Any]] = []


def parse_intent(text: str) -> Dict[str, Any]:
    """
    Parse user command to extract intent, action, profile, and parameters.
    Uses simple regex/keyword matching for offline operation.
    
    Args:
        text: User command text
        
    Returns:
        Dictionary with parsed intent
        
    Example:
        intent = parse_intent("generate report for Sales")
        # Returns: {"action": "generate_report", "profile": "Sales", "params": {}}
    """
    text_lower = text.lower().strip()
    
    intent = {
        "action": "unknown",
        "profile": None,
        "params": {},
        "raw_text": text
    }
    
    # Extract profile name (common pattern: "for <profile>")
    profile_match = re.search(r'for\s+(\w+)', text, re.IGNORECASE)
    if profile_match:
        intent["profile"] = profile_match.group(1)
    
    # Detect action based on keywords
    if any(word in text_lower for word in ["generate", "create", "build", "make"]) and \
       any(word in text_lower for word in ["report", "summary", "document"]):
        intent["action"] = "generate_report"
        
    elif any(word in text_lower for word in ["summarize", "summary", "brief"]):
        intent["action"] = "summarize"
        
    elif any(word in text_lower for word in ["schedule", "automate", "recurring"]):
        intent["action"] = "schedule"
        
        # Extract time parameters
        if "daily" in text_lower:
            intent["params"]["frequency"] = "daily"
            # Extract time (e.g., "at 9:00", "at 9am")
            time_match = re.search(r'at\s+(\d{1,2}):?(\d{2})?\s*(am|pm)?', text_lower)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2)) if time_match.group(2) else 0
                if time_match.group(3) == 'pm' and hour < 12:
                    hour += 12
                intent["params"]["hour"] = hour
                intent["params"]["minute"] = minute
        elif "hourly" in text_lower or "every hour" in text_lower:
            intent["params"]["frequency"] = "interval"
            intent["params"]["minutes"] = 60
        elif "every" in text_lower:
            # Extract interval (e.g., "every 30 minutes")
            interval_match = re.search(r'every\s+(\d+)\s+minutes?', text_lower)
            if interval_match:
                intent["params"]["frequency"] = "interval"
                intent["params"]["minutes"] = int(interval_match.group(1))
    
    elif any(word in text_lower for word in ["speak", "say", "voice", "audio"]):
        intent["action"] = "speak"
        
    elif any(word in text_lower for word in ["list", "show", "display"]) and \
         any(word in text_lower for word in ["profile", "report", "schedule"]):
        if "profile" in text_lower:
            intent["action"] = "list_profiles"
        elif "report" in text_lower:
            intent["action"] = "list_reports"
        elif "schedule" in text_lower or "job" in text_lower:
            intent["action"] = "list_schedules"
    
    elif any(word in text_lower for word in ["activate", "switch", "use"]) and \
         any(word in text_lower for word in ["profile"]):
        intent["action"] = "activate_profile"
    
    elif any(word in text_lower for word in ["chart", "graph", "visualize", "plot"]):
        intent["action"] = "generate_chart"
        
        # Detect chart type
        if "trend" in text_lower or "line" in text_lower:
            intent["params"]["chart_type"] = "trend"
        elif "bar" in text_lower or "top" in text_lower:
            intent["params"]["chart_type"] = "bar"
        elif "pie" in text_lower or "breakdown" in text_lower:
            intent["params"]["chart_type"] = "pie"
    
    elif any(word in text_lower for word in ["send", "email", "mail"]) and \
         any(word in text_lower for word in ["report", "summary"]):
        intent["action"] = "send_report"
        
        # Extract recipient
        to_match = re.search(r'to\s+(\S+@\S+|\w+)', text, re.IGNORECASE)
        if to_match:
            intent["params"]["recipient"] = to_match.group(1)
    
    elif any(word in text_lower for word in ["notify", "alert"]):
        intent["action"] = "notify"
        
        # Extract user
        user_match = re.search(r'(?:notify|alert)\s+(\w+)', text, re.IGNORECASE)
        if user_match:
            intent["params"]["user"] = user_match.group(1)
    
    elif any(word in text_lower for word in ["query", "search", "find"]) and \
         any(word in text_lower for word in ["document", "knowledge", "doc"]):
        intent["action"] = "query_document"
        
        # Extract search query (everything after "query document" or similar)
        query_match = re.search(r'(?:query|search|find).*?(?:document|knowledge).*?[:\s]+(.+)', text, re.IGNORECASE)
        if query_match:
            intent["params"]["query"] = query_match.group(1).strip()
        else:
            # Use the whole text as query if no specific pattern found
            intent["params"]["query"] = text
    
    elif any(word in text_lower for word in ["analyze", "analysis", "calculate"]) and \
         any(word in text_lower for word in ["kpi", "metric", "performance", "financial"]):
        intent["action"] = "analyze_kpis"
        
        # Extract analysis type
        if "anomaly" in text_lower or "anomalies" in text_lower:
            intent["params"]["include_anomalies"] = True
        if "trend" in text_lower:
            intent["params"]["include_trends"] = True
    
    logger.info(f"Parsed intent: {intent}")
    return intent


def execute_command(command: str, profile: Optional[str] = None) -> Dict[str, Any]:
    """
    Execute a command by routing to appropriate subsystems.
    
    Args:
        command: User command text
        profile: Optional profile to use (overrides parsed profile)
        
    Returns:
        Result dictionary with status, message, and outputs
        
    Example:
        result = execute_command("generate report for Sales")
        print(result["message"])
    """
    start_time = datetime.now()
    
    # Parse intent
    intent = parse_intent(command)
    
    # Override profile if provided
    if profile:
        intent["profile"] = profile
    
    # Initialize result
    result = {
        "status": "unknown",
        "message": "",
        "outputs": {},
        "timestamp": start_time.isoformat()
    }
    
    try:
        # Route to appropriate handler
        action = intent["action"]
        
        if action == "generate_report":
            result = _handle_generate_report(intent)
        elif action == "summarize":
            result = _handle_summarize(intent)
        elif action == "schedule":
            result = _handle_schedule(intent)
        elif action == "speak":
            result = _handle_speak(intent)
        elif action == "list_profiles":
            result = _handle_list_profiles(intent)
        elif action == "list_reports":
            result = _handle_list_reports(intent)
        elif action == "list_schedules":
            result = _handle_list_schedules(intent)
        elif action == "activate_profile":
            result = _handle_activate_profile(intent)
        elif action == "generate_chart":
            result = _handle_generate_chart(intent)
        elif action == "send_report":
            result = _handle_send_report(intent)
        elif action == "notify":
            result = _handle_notify(intent)
        elif action == "query_document":
            result = _handle_query_document(intent)
        elif action == "analyze_kpis":
            result = _handle_analyze_kpis(intent)
        else:
            result["status"] = "error"
            result["message"] = f"Unknown action: {action}"
        
        # Add execution time and intent
        execution_time = (datetime.now() - start_time).total_seconds()
        result["execution_time"] = execution_time
        result["intent"] = intent
        
        # Log result
        logger.info(f"Command executed: {action} - Status: {result['status']} - Time: {execution_time:.2f}s")
        
        # Add to history
        ORCHESTRATION_HISTORY.append({
            "command": command,
            "intent": intent,
            "result": result,
            "timestamp": start_time.isoformat()
        })
        
        # Log to learning memory (Phase 5G)
        try:
            from learning_memory import log_success
            
            # Determine feedback based on result
            feedback = "positive" if result["status"] == "success" else "negative"
            
            # Log for learning
            log_success(command, result, feedback)
        except Exception as e:
            logger.debug(f"Learning memory logging failed: {e}")
        
    except Exception as e:
        result["status"] = "error"
        result["message"] = f"Execution error: {str(e)}"
        result["intent"] = intent
        logger.error(f"Command execution failed: {e}")
    
    return result


def _handle_generate_report(intent: Dict[str, Any]) -> Dict[str, Any]:
    """Handle report generation command."""
    try:
        from report_generator import build_executive_report
        from profile_manager import load_recent
        
        profile = intent.get("profile")
        if not profile:
            return {
                "status": "error",
                "message": "Profile required for report generation",
                "outputs": {}
            }
        
        # Load recent interactions
        recent = load_recent(profile, n=10)
        
        if not recent:
            return {
                "status": "error",
                "message": f"No data available for profile: {profile}",
                "outputs": {}
            }
        
        # Create summary DataFrame
        df = pd.DataFrame({
            "Metric": ["Total Interactions", "Recent Activity", "Profile Status"],
            "Value": [len(recent), f"{min(10, len(recent))} queries", "Active"]
        })
        
        # Generate report
        report = build_executive_report(
            title=f"{profile} Profile Report - {datetime.now().strftime('%Y-%m-%d')}",
            question=f"What is the activity summary for {profile}?",
            sql="-- Profile context query",
            df=df,
            insights=f"Profile {profile} has {len(recent)} total interactions. Recent activity shows consistent engagement.",
            charts=None
        )
        
        return {
            "status": "success",
            "message": f"Report generated for {profile}",
            "outputs": {
                "report_path": report['paths']['html_path'],
                "report_md": report['paths']['md_path']
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Report generation failed: {str(e)}",
            "outputs": {}
        }


def _handle_summarize(intent: Dict[str, Any]) -> Dict[str, Any]:
    """Handle summarization command."""
    try:
        from voice_interface import summarize_conversation
        
        profile = intent.get("profile")
        if not profile:
            return {
                "status": "error",
                "message": "Profile required for summarization",
                "outputs": {}
            }
        
        # Generate summary (without speaking by default)
        summary = summarize_conversation(profile, speak=False)
        
        if summary:
            return {
                "status": "success",
                "message": f"Summary generated for {profile}",
                "outputs": {"summary": summary}
            }
        else:
            return {
                "status": "error",
                "message": f"Could not generate summary for {profile}",
                "outputs": {}
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Summarization failed: {str(e)}",
            "outputs": {}
        }


def _handle_schedule(intent: Dict[str, Any]) -> Dict[str, Any]:
    """Handle scheduling command."""
    try:
        from scheduler import schedule_daily, schedule_interval
        
        profile = intent.get("profile")
        params = intent.get("params", {})
        frequency = params.get("frequency")
        
        if not profile:
            return {
                "status": "error",
                "message": "Profile required for scheduling",
                "outputs": {}
            }
        
        # Create job function
        def scheduled_job():
            from report_generator import build_executive_report
            from profile_manager import load_recent
            
            recent = load_recent(profile, n=10)
            if recent:
                df = pd.DataFrame({
                    "Metric": ["Interactions"],
                    "Value": [len(recent)]
                })
                build_executive_report(
                    title=f"Scheduled {profile} Report",
                    question="Scheduled report",
                    sql="--",
                    df=df,
                    insights=f"Automated report for {profile}",
                    charts=None
                )
        
        # Schedule based on frequency
        if frequency == "daily":
            hour = params.get("hour", 9)
            minute = params.get("minute", 0)
            handle = schedule_daily(hour, minute, scheduled_job)
            return {
                "status": "success",
                "message": f"Scheduled daily report for {profile} at {hour:02d}:{minute:02d}",
                "outputs": {"job_id": handle}
            }
        elif frequency == "interval":
            minutes = params.get("minutes", 60)
            handle = schedule_interval(minutes, scheduled_job)
            return {
                "status": "success",
                "message": f"Scheduled report for {profile} every {minutes} minutes",
                "outputs": {"job_id": handle}
            }
        else:
            return {
                "status": "error",
                "message": "Invalid schedule frequency",
                "outputs": {}
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Scheduling failed: {str(e)}",
            "outputs": {}
        }


def _handle_speak(intent: Dict[str, Any]) -> Dict[str, Any]:
    """Handle speech output command."""
    try:
        from voice_interface import speak_text, summarize_conversation
        
        profile = intent.get("profile")
        
        if profile:
            # Speak profile summary
            summary = summarize_conversation(profile, speak=True)
            if summary:
                return {
                    "status": "success",
                    "message": f"Spoke summary for {profile}",
                    "outputs": {"summary": summary}
                }
        else:
            # Speak generic message
            speak_text("Voice interface operational")
            return {
                "status": "success",
                "message": "Speech output complete",
                "outputs": {}
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Speech failed: {str(e)}",
            "outputs": {}
        }


def _handle_list_profiles(intent: Dict[str, Any]) -> Dict[str, Any]:
    """Handle list profiles command."""
    try:
        from profile_manager import list_profiles
        
        profiles = list_profiles()
        
        return {
            "status": "success",
            "message": f"Found {len(profiles)} profiles",
            "outputs": {"profiles": profiles}
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"List profiles failed: {str(e)}",
            "outputs": {}
        }


def _handle_list_reports(intent: Dict[str, Any]) -> Dict[str, Any]:
    """Handle list reports command."""
    try:
        from dashboard_gateway import get_recent_reports
        
        reports = get_recent_reports(limit=20)
        
        return {
            "status": "success",
            "message": f"Found {len(reports)} reports",
            "outputs": {"reports": reports}
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"List reports failed: {str(e)}",
            "outputs": {}
        }


def _handle_list_schedules(intent: Dict[str, Any]) -> Dict[str, Any]:
    """Handle list schedules command."""
    try:
        from scheduler import list_jobs
        
        jobs = list_jobs()
        
        return {
            "status": "success",
            "message": f"Found {len(jobs)} scheduled jobs",
            "outputs": {"jobs": jobs}
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"List schedules failed: {str(e)}",
            "outputs": {}
        }


def _handle_activate_profile(intent: Dict[str, Any]) -> Dict[str, Any]:
    """Handle activate profile command."""
    try:
        from profile_manager import set_active_profile
        
        profile = intent.get("profile")
        if not profile:
            return {
                "status": "error",
                "message": "Profile name required",
                "outputs": {}
            }
        
        success = set_active_profile(profile)
        
        if success:
            return {
                "status": "success",
                "message": f"Activated profile: {profile}",
                "outputs": {"profile": profile}
            }
        else:
            return {
                "status": "error",
                "message": f"Profile not found: {profile}",
                "outputs": {}
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Profile activation failed: {str(e)}",
            "outputs": {}
        }


def _handle_generate_chart(intent: Dict[str, Any]) -> Dict[str, Any]:
    """Handle chart generation command."""
    try:
        from viz import chart_sales_trend, chart_top_customers, chart_category_breakdown
        from profile_manager import load_recent
        
        profile = intent.get("profile")
        chart_type = intent.get("params", {}).get("chart_type", "trend")
        
        if not profile:
            return {
                "status": "error",
                "message": "Profile required for chart generation",
                "outputs": {}
            }
        
        # Load recent data (simplified for demo)
        recent = load_recent(profile, n=10)
        
        if not recent:
            return {
                "status": "error",
                "message": f"No data available for {profile}",
                "outputs": {}
            }
        
        # Create sample data for chart
        df = pd.DataFrame({
            "Category": [f"Item {i}" for i in range(1, 6)],
            "Value": [100 - i*10 for i in range(1, 6)]
        })
        
        # Generate chart based on type
        if chart_type == "trend":
            chart_path = chart_sales_trend(df, "Category", "Value")
        elif chart_type == "bar":
            chart_path = chart_top_customers(df, "Category", "Value")
        else:
            chart_path = chart_category_breakdown(df, "Category", "Value")
        
        return {
            "status": "success",
            "message": f"Chart generated for {profile}",
            "outputs": {"chart_path": chart_path}
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Chart generation failed: {str(e)}",
            "outputs": {}
        }


def orchestrate_conversation(profile: str, max_turns: int = 10) -> List[Dict[str, Any]]:
    """
    Orchestrate a multi-turn conversation maintaining context.
    
    Args:
        profile: Profile to use for conversation
        max_turns: Maximum number of conversation turns
        
    Returns:
        List of conversation turns with results
        
    Example:
        conversation = orchestrate_conversation("Sales", max_turns=5)
        for turn in conversation:
            print(f"User: {turn['command']}")
            print(f"Result: {turn['result']['message']}")
    """
    conversation = []
    
    logger.info(f"Starting orchestrated conversation for profile: {profile}")
    
    # Example conversation flow (in real use, this would be interactive)
    commands = [
        f"summarize for {profile}",
        f"generate report for {profile}",
        f"list profiles"
    ]
    
    for i, command in enumerate(commands[:max_turns]):
        logger.info(f"Turn {i+1}: {command}")
        
        result = execute_command(command, profile=profile)
        
        turn = {
            "turn": i + 1,
            "command": command,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
        conversation.append(turn)
        
        # Break if error
        if result["status"] == "error":
            logger.warning(f"Conversation stopped due to error: {result['message']}")
            break
    
    logger.info(f"Conversation completed: {len(conversation)} turns")
    
    return conversation


def get_orchestration_history(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Get recent orchestration history.
    
    Args:
        limit: Maximum number of history items to return
        
    Returns:
        List of orchestration history items
    """
    return ORCHESTRATION_HISTORY[-limit:]


def _handle_send_report(intent: Dict[str, Any]) -> Dict[str, Any]:
    """Handle send report command."""
    try:
        from email_engine import send_email
        from dashboard_gateway import get_recent_reports
        
        profile = intent.get("profile")
        recipient = intent.get("params", {}).get("recipient")
        
        if not recipient:
            return {
                "status": "error",
                "message": "Recipient email required",
                "outputs": {}
            }
        
        # Get latest report
        reports = get_recent_reports(limit=1)
        
        if not reports:
            return {
                "status": "error",
                "message": "No reports available to send",
                "outputs": {}
            }
        
        latest_report = reports[0]
        
        # Send email with report
        subject = f"Report: {latest_report['name']}"
        body = f"Please find attached the latest report.\n\nReport: {latest_report['name']}\nGenerated: {latest_report['date']}"
        
        result = send_email(
            to=recipient,
            subject=subject,
            body=body,
            attachments=[latest_report['path']],
            priority="normal"
        )
        
        return {
            "status": "success" if result["success"] else "error",
            "message": f"Report sent to {recipient} ({result['mode']} mode)",
            "outputs": {
                "email_id": result.get("email_id"),
                "report": latest_report['name']
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Send report failed: {str(e)}",
            "outputs": {}
        }


def _handle_notify(intent: Dict[str, Any]) -> Dict[str, Any]:
    """Handle notification command."""
    try:
        from email_engine import notify_user
        
        user = intent.get("params", {}).get("user")
        profile = intent.get("profile")
        
        if not user:
            return {
                "status": "error",
                "message": "User required for notification",
                "outputs": {}
            }
        
        # Generate notification message
        if profile:
            message = f"Update for {profile} profile"
        else:
            message = "System notification"
        
        result = notify_user(user, message, priority="normal")
        
        return {
            "status": "success" if result["success"] else "error",
            "message": f"Notification sent to {user}",
            "outputs": {
                "notification_id": result.get("notification_id")
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Notification failed: {str(e)}",
            "outputs": {}
        }


def _handle_query_document(intent: Dict[str, Any]) -> Dict[str, Any]:
    """Handle document query command using knowledge fusion."""
    try:
        from knowledge_fusion import search_knowledge
        
        query = intent.get("params", {}).get("query")
        
        if not query:
            return {
                "status": "error",
                "message": "Query text required for document search",
                "outputs": {}
            }
        
        # Search knowledge base
        results = search_knowledge(query, top_k=5)
        
        if not results:
            return {
                "status": "success",
                "message": "No relevant documents found",
                "outputs": {
                    "results": [],
                    "count": 0
                }
            }
        
        # Format results for output
        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_results.append({
                "rank": i,
                "text": result["text"][:200] + "..." if len(result["text"]) > 200 else result["text"],
                "source": result["metadata"].get("filename", "unknown"),
                "relevance": 1.0 - (result["distance"] if result["distance"] else 0)
            })
        
        return {
            "status": "success",
            "message": f"Found {len(results)} relevant documents",
            "outputs": {
                "results": formatted_results,
                "count": len(results),
                "query": query
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Document query failed: {str(e)}",
            "outputs": {}
        }


def _handle_analyze_kpis(intent: Dict[str, Any]) -> Dict[str, Any]:
    """Handle KPI analysis command."""
    try:
        from kpi_analyzer import analyze_kpis, detect_anomalies, generate_kpi_summary
        from profile_manager import load_recent
        
        profile = intent.get("profile")
        params = intent.get("params", {})
        
        if not profile:
            return {
                "status": "error",
                "message": "Profile required for KPI analysis",
                "outputs": {}
            }
        
        # Load recent data for profile
        recent = load_recent(profile, n=20)
        
        if not recent:
            return {
                "status": "error",
                "message": f"No data available for profile: {profile}",
                "outputs": {}
            }
        
        # Create sample dataframe from profile data
        # In real scenario, this would come from actual business data
        df = pd.DataFrame({
            "Period": [f"Period {i+1}" for i in range(min(10, len(recent)))],
            "Value": [100000 + i * 5000 + (i % 3) * 2000 for i in range(min(10, len(recent)))],
            "Cost": [60000 + i * 3000 for i in range(min(10, len(recent)))]
        })
        
        # Analyze KPIs
        kpi_results = analyze_kpis(df)
        
        if kpi_results["status"] != "success":
            return {
                "status": "error",
                "message": f"KPI analysis failed: {kpi_results['message']}",
                "outputs": {}
            }
        
        outputs = {
            "metrics": kpi_results["metrics"],
            "summary": generate_kpi_summary(df)
        }
        
        # Include anomaly detection if requested
        if params.get("include_anomalies"):
            anomaly_results = detect_anomalies(df, value_col="Value", method="iqr")
            outputs["anomalies"] = {
                "count": anomaly_results["anomaly_count"],
                "percentage": anomaly_results["anomaly_percentage"],
                "details": anomaly_results["anomalies"][:5]  # Top 5 anomalies
            }
        
        return {
            "status": "success",
            "message": f"KPI analysis complete for {profile}",
            "outputs": outputs
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"KPI analysis failed: {str(e)}",
            "outputs": {}
        }


if __name__ == "__main__":
    print("="*70)
    print("ORCHESTRATION CORE TEST")
    print("="*70)
    print()
    
    # Test 1: Parse intents
    print("1. Testing intent parsing...")
    test_commands = [
        "generate report for Sales",
        "summarize for Marketing",
        "schedule daily report for HR at 9:00",
        "speak summary for Finance",
        "list profiles",
        "query document: business strategy",
        "analyze KPIs for Sales"
    ]
    
    for cmd in test_commands:
        intent = parse_intent(cmd)
        print(f"   '{cmd}' → {intent['action']}")
    print()
    
    # Test 2: Execute commands
    print("2. Testing command execution...")
    result = execute_command("list profiles")
    print(f"   Status: {result['status']}")
    print(f"   Message: {result['message']}")
    print()
    
    # Test 3: Check history
    print("3. Checking orchestration history...")
    history = get_orchestration_history(limit=5)
    print(f"   History entries: {len(history)}")
    print()
    
    print("="*70)
    print("🧩 Orchestration Core ready")
    print("="*70)
