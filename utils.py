import re

def is_greeting(message):
    greetings = [
        "hello", "hi", "hey", "good morning", "good afternoon", "good evening", "howdy", "hiya",
        "sup", "what's up", "yo", "g'day", "morning"
    ]
    # Check if the message is exactly one of the greetings
    if message.lower() in greetings:
        return True
    return False

def is_sql_query(text):
    """
    Check if the text is a valid SQL query.
    Must start with a SQL command keyword to be considered valid SQL.
    """
    if not text or not isinstance(text, str):
        return False
    
    # Remove leading/trailing whitespace and convert to lowercase
    text_stripped = text.strip().lower()
    
    # SQL queries must start with one of these keywords
    sql_start_keywords = [
        "select", "insert", "update", "delete", "create", "drop", 
        "alter", "show", "describe", "explain", "with"
    ]
    
    # Check if the text starts with a SQL keyword
    for keyword in sql_start_keywords:
        if text_stripped.startswith(keyword + " ") or text_stripped == keyword:
            return True
    
    return False
