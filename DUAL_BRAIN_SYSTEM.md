# Dual-Brain Intelligence System

## Overview

The Vanna-AI-for-SQL project has been upgraded to a **Dual-Brain Intelligent System** that seamlessly handles both:
1. **Data-driven SQL queries** (Vanna Brain)
2. **General conversational questions** (Mistral Brain)

## Architecture

### 🧠 Brain #1: SQL Brain (Vanna)
- **Purpose**: Handles all database-related queries
- **Technology**: Vanna + MySQL + ChromaDB + Mistral 7B
- **Triggers**: Questions containing keywords like customer, sales, employee, order, etc.
- **Output**: SQL queries + Natural language summaries of data

### 🧠 Brain #2: General Intelligence Brain (Mistral)
- **Purpose**: Handles open-domain conversational queries
- **Technology**: Ollama with Mistral 7B Instruct
- **Triggers**: Questions about general knowledge, explanations, history, technology, etc.
- **Output**: Conversational responses similar to ChatGPT

## Key Features

### ✅ Automatic Query Routing
The system automatically classifies each question and routes it to the appropriate brain:

**SQL Brain Examples:**
- "What is the phone number of Priya Sharma?"
- "List all customers in Mumbai"
- "Show me employees in HR department"
- "What is the average salary?"

**General Brain Examples:**
- "What is Lenovo?"
- "Explain HTML, CSS, and JavaScript"
- "Who won the last cricket world cup?"
- "Tell me about artificial intelligence"

### ✅ Conversational Context Memory
- Maintains conversation history (last 10 messages)
- Enables follow-up questions with context
- Example:
  - User: "What is Lenovo?"
  - AI: "Lenovo is a multinational technology company..."
  - User: "Where is it headquartered?"
  - AI: "Lenovo is headquartered in Beijing, China..."

### ✅ Seamless Brain Switching
The system switches between brains automatically within the same conversation:
1. "What is the phone number of Priya Sharma?" → SQL Brain
2. "Tell me about Lenovo company" → General Brain
3. "List all customers in Mumbai" → SQL Brain
4. "Who won the last cricket world cup?" → General Brain

## Implementation Details

### Files Added/Modified

**New Files:**
- `query_router.py` - Core routing logic and brain classification

**Modified Files:**
- `ad_ai_app.py` - Integrated dual-brain routing into the Flask app

### Query Classification Logic

The router uses keyword matching to classify queries:

```python
sql_keywords = [
    "customer", "order", "sales", "employee", "department",
    "table", "query", "data", "sql", "industry", "amount",
    "total", "average", "count", "record", "show", "list",
    "phone", "email", "address", "contact", "manager",
    "city", "product", "revenue", "profit", "salary"
]
```

If any SQL keyword is found → SQL Brain
Otherwise → General Brain

### Context Memory Implementation

- Stores last 10 messages (5 exchanges) in conversation history
- Prepends context to each query for the General Brain
- Enables natural follow-up questions

## Testing

### Test Cases

Run `python test_dual_brain.py` to verify:

1. ✓ Query classification accuracy
2. ✓ SQL brain routing
3. ✓ General brain routing
4. ✓ Response generation

### Manual Testing

Access the app at **http://127.0.0.1:5000** and try:

**Sequence 1: Mixed Queries**
1. "What is the phone number of Priya Sharma?" → SQL result
2. "Tell me about Lenovo company" → General knowledge
3. "And where is Lenovo headquartered?" → Uses context
4. "List all customers in Mumbai" → SQL result

**Sequence 2: Follow-up Questions**
1. "What is HTML?" → General explanation
2. "How is it different from CSS?" → Uses context
3. "Show me all employees" → Switches to SQL

## Configuration

### Models Used
- **SQL Brain**: Mistral 7B Instruct (via Vanna)
- **General Brain**: Mistral 7B Instruct (via Ollama)

### Database
- **Type**: MySQL/MariaDB
- **Database**: ad_ai_testdb
- **Host**: localhost:3306

### Vector Store
- **Type**: ChromaDB
- **Path**: vanna_chroma_db/

## Benefits

1. **Unified Interface**: Single chat interface for both data queries and general questions
2. **Context Awareness**: Remembers conversation history for natural follow-ups
3. **Intelligent Routing**: Automatically selects the right brain for each query
4. **No User Training**: Users don't need to specify which brain to use
5. **Seamless Experience**: Switches between brains transparently

## Future Enhancements

Potential improvements:
- Add more sophisticated NLP for query classification
- Implement long-term memory across sessions
- Add support for multi-turn SQL queries
- Integrate web search for real-time information
- Add voice input/output capabilities

## Troubleshooting

**Issue**: General brain not responding
- **Solution**: Ensure Ollama is running and Mistral model is installed
- **Command**: `ollama pull mistral:7b-instruct`

**Issue**: SQL queries failing
- **Solution**: Verify MySQL is running and database is accessible
- **Command**: `python -c "import mysql.connector; conn = mysql.connector.connect(host='localhost', user='root', password='', database='ad_ai_testdb'); print('Connected!')"`

**Issue**: Context not working
- **Solution**: Check that conversation history is being saved to JSON files
- **Location**: `conversations/` directory

## Conclusion

The Dual-Brain Intelligence System transforms the Vanna-AI-for-SQL project into a comprehensive AI assistant that can handle both structured data queries and open-domain conversations, all while maintaining context and providing a seamless user experience.
