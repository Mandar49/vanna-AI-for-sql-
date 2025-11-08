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
    # A simple but more robust check for SQL queries.
    sql_keywords = [
        "select", "from", "where", "insert", "update", "delete", "create",
        "drop", "alter", "table", "database", "index", "view", "join",
        "inner join", "left join", "right join", "on", "group by", "order by",
        "having", "limit", "offset", "union", "distinct", "as", "count",
        "sum", "avg", "min", "max", "like", "in", "between", "and", "or", "not"
    ]

    # Normalize the text to lower case and check for presence of keywords
    text_lower = text.lower()
    for keyword in sql_keywords:
        # Using regex to match whole words to avoid matching substrings in other words
        if re.search(r'\b' + keyword + r'\b', text_lower):
            return True
    return False
