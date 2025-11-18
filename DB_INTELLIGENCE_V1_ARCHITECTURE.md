# DB-INTELLIGENCE-V1 System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                    (Flask Web Application)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      QUERY ROUTER                               │
│                  (Hybrid Intent Detection)                      │
│  • SQL vs General Knowledge Classification                      │
│  • Person Query Detection                                       │
│  • Context-Aware Routing                                        │
└─────┬───────────────────────┬───────────────────────┬───────────┘
      │                       │                       │
      ▼                       ▼                       ▼
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐
│  SQL PATH   │      │ GENERAL PATH │      │  PERSON PATH    │
└─────────────┘      └──────────────┘      └─────────────────┘
      │                       │                       │
      ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PROCESSING LAYER                             │
├─────────────────────┬───────────────────┬───────────────────────┤
│   SQL EXECUTION     │  HYBRID REASONER  │  DATABASE LOOKUP      │
│   • Vanna AI        │  • 6 Frameworks   │  • Person Search      │
│   • SQL Corrector   │  • Empty Handler  │  • Data Retrieval     │
│   • Retry Logic     │  • Knowledge Base │  • Result Format      │
└─────────┬───────────┴─────────┬─────────┴───────────┬───────────┘
          │                     │                     │
          ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                   BUSINESS ANALYST                              │
│              (Hybrid Intelligence Engine)                       │
│  • analyze_with_hybrid_intelligence()                           │
│  • SQL Result Interpretation                                    │
│  • Framework Application                                        │
│  • Strategic Recommendations                                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   RESPONSE COMPOSER                             │
│              (Output Formatting Layer)                          │
│  • compose_hybrid_response()                                    │
│  • compose_general_answer()                                     │
│  • Plain Text Formatting                                        │
│  • Mode Selection (COMPACT/DETAILED)                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CONTEXT MEMORY                               │
│  • Conversation History                                         │
│  • Profile Management                                           │
│  • Interaction Logging                                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FINAL RESPONSE                             │
│         SQL RESULT → INSIGHT → RECOMMENDATION                   │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Query Router (query_router.py)

**Responsibilities:**
- Detect query intent (SQL, general, person)
- Route to appropriate processing path
- Integrate hybrid reasoner for classification

**Key Methods:**
```python
classify_query(question) → 'sql' | 'general' | 'person'
route_query(question, history) → routing_result
_handle_general_query(question) → answer
```

### 2. Hybrid Reasoner (hybrid_reasoner.py)

**Responsibilities:**
- Business framework application
- Empty result interpretation
- General knowledge answering
- Strategic recommendation generation

**Business Frameworks:**
1. RFM Analysis (Customer Segmentation)
2. Cohort Analysis (Retention Tracking)
3. Margin-Volume Matrix (Product Strategy)
4. Growth-Stability Matrix (Risk Management)
5. Retention Strategy (Lifecycle Management)
6. SWOT Analysis (Strategic Planning)

**Key Methods:**
```python
interpret_result(sql_result, context, question) → {insight, recommendation}
should_use_sql(question) → bool
answer_general_question(question) → answer
_detect_framework(question) → framework_name
```

### 3. Business Analyst (business_analyst.py)

**Responsibilities:**
- Hybrid intelligence analysis
- SQL result interpretation
- Trend detection
- CAGR and forecast calculations

**Key Methods:**
```python
analyze_with_hybrid_intelligence(question, df, sql) → analysis
analyze_results_with_llm(question, df, sql) → analysis
detect_trend(series) → 'upward' | 'downward' | 'stable'
```

### 4. Response Composer (response_composer.py)

**Responsibilities:**
- Format hybrid responses
- Plain text output (no markdown)
- Mode selection (COMPACT/DETAILED)
- Section formatting

**Key Methods:**
```python
compose_hybrid_response(sql_result, insight, recommendation, sql_query) → formatted
compose_general_answer(answer) → formatted
set_mode(mode) → None
```

### 5. SQL Corrector (sql_corrector.py)

**Responsibilities:**
- SQL execution with retry
- Error correction
- CAGR calculations
- Forecast generation

**Key Methods:**
```python
execute_with_retry(sql, max_retries) → execution_result
calculate_cagr_sql(start_year, end_year, forecast_years) → cagr_result
```

## Data Flow Diagrams

### SQL Query Flow

```
User Question: "What are total sales by year?"
        ↓
Query Router → Detects: SQL query needed
        ↓
Vanna AI → Generates SQL
        ↓
SQL Corrector → Executes with retry
        ↓
        ├─→ Success: Returns DataFrame
        │        ↓
        │   Business Analyst → Hybrid Analysis
        │        ↓
        │   Hybrid Reasoner → Apply Framework
        │        ↓
        │   Response Composer → Format Output
        │        ↓
        │   SQL RESULT
        │   INSIGHT
        │   STRATEGIC RECOMMENDATION
        │   SQL QUERY EXECUTED
        │
        └─→ Failure: Returns error
                 ↓
            Hybrid Reasoner → Interpret error
                 ↓
            Response Composer → Format with reasoning
                 ↓
            SQL RESULT (error)
            INSIGHT (why it failed)
            STRATEGIC RECOMMENDATION (what to do)
```

### General Knowledge Flow

```
User Question: "What is customer churn?"
        ↓
Query Router → Detects: General knowledge
        ↓
Hybrid Reasoner → answer_general_question()
        ↓
Response Composer → compose_general_answer()
        ↓
ANSWER
(Definition + explanation)
```

### Empty Result Flow

```
User Question: "Show customers with >10 orders"
        ↓
Query Router → Detects: SQL query needed
        ↓
SQL Execution → Returns empty DataFrame
        ↓
Business Analyst → analyze_with_hybrid_intelligence()
        ↓
Hybrid Reasoner → _handle_empty_result()
        ↓
        ├─→ _reason_about_empty_data()
        │   "No repeat customers = retention challenge"
        │
        └─→ _suggest_next_action()
            "Implement loyalty programs..."
        ↓
Response Composer → compose_hybrid_response()
        ↓
SQL RESULT: No data found
INSIGHT: Retention challenge explanation
STRATEGIC RECOMMENDATION: Actionable steps
```

## Integration Points

### Database Layer
```
MySQL Database
    ↓
SQL Corrector (mysql.connector)
    ↓
Pandas DataFrame
    ↓
Business Analyst
```

### LLM Layer
```
Ollama (Mistral 7B)
    ↓
Vanna AI (SQL Generation)
    ↓
Business Analyst (Analysis)
    ↓
Response Composer (Formatting)
```

### Memory Layer
```
Context Memory
    ↓
Profile Manager
    ↓
Conversation History
    ↓
Query Router (context-aware)
```

## Output Format Specification

### SQL Query Output
```
────────────────────────────────────────────────────────────
SQL RESULT
────────────────────────────────────────────────────────────
<actual data or "No data found">

────────────────────────────────────────────────────────────
INSIGHT
────────────────────────────────────────────────────────────
<business interpretation using ONLY SQL data>

────────────────────────────────────────────────────────────
STRATEGIC RECOMMENDATION
────────────────────────────────────────────────────────────
<actionable next steps, frameworks, decisions>

────────────────────────────────────────────────────────────
SQL QUERY EXECUTED
────────────────────────────────────────────────────────────
<actual SQL query>
```

### General Knowledge Output
```
────────────────────────────────────────────────────────────
ANSWER
────────────────────────────────────────────────────────────
<knowledgeable response with reasoning>
```

## Error Handling Architecture

```
Error Occurs
    ↓
Error Logger → Log details
    ↓
SQL Corrector → Attempt correction
    ↓
    ├─→ Success: Continue normal flow
    │
    └─→ Failure: Hybrid reasoning
            ↓
        Hybrid Reasoner → Interpret error
            ↓
        Response Composer → Format with guidance
            ↓
        User receives actionable feedback
```

## Performance Optimization

### Caching Strategy
```
Query Cache
    ↓
Check if query seen before
    ↓
    ├─→ Cache Hit: Return cached result
    │
    └─→ Cache Miss: Execute query
            ↓
        Store in cache
```

### Framework Selection
```
Question Analysis
    ↓
Keyword Detection
    ↓
Framework Selection (O(1))
    ↓
Apply Framework
```

## Security Architecture

### SQL Injection Prevention
```
User Input
    ↓
Vanna AI (Parameterized SQL)
    ↓
SQL Corrector (Validation)
    ↓
MySQL Connector (Prepared Statements)
```

### Data Access Control
```
Profile Manager
    ↓
Authentication Check
    ↓
Authorization Verification
    ↓
Data Access
```

## Scalability Considerations

### Horizontal Scaling
- Stateless application design
- Session management via external store
- Load balancer compatible

### Vertical Scaling
- Efficient DataFrame operations
- Lazy evaluation where possible
- Memory-conscious caching

### Database Scaling
- Connection pooling
- Query optimization
- Index recommendations

## Monitoring Points

### Key Metrics
1. Query response time
2. SQL execution success rate
3. Framework detection accuracy
4. Empty result rate
5. User satisfaction score

### Logging Levels
```
ERROR   → SQL failures, system errors
WARNING → Empty results, slow queries
INFO    → Query routing, framework selection
DEBUG   → Detailed execution flow
```

## Deployment Architecture

### Development
```
Local Machine
    ↓
Flask Dev Server (port 5000)
    ↓
Local MySQL Database
```

### Production
```
Load Balancer
    ↓
Multiple Flask Instances
    ↓
MySQL Cluster (Read Replicas)
    ↓
Redis Cache
```

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Web Framework | Flask |
| Database | MySQL |
| ORM/Query | Pandas, mysql.connector |
| AI/LLM | Ollama (Mistral 7B), Vanna AI |
| Caching | In-memory (upgradeable to Redis) |
| Testing | Python unittest |
| Documentation | Markdown |

## File Structure

```
project/
├── ad_ai_app_hybrid.py          # Main application
├── hybrid_reasoner.py           # Business intelligence engine
├── query_router.py              # Enhanced routing
├── business_analyst.py          # Enhanced analysis
├── response_composer.py         # Enhanced formatting
├── sql_corrector.py             # SQL execution
├── context_memory.py            # Memory management
├── profile_manager.py           # Profile management
├── test_hybrid_intelligence.py  # Test suite
└── docs/
    ├── DB_INTELLIGENCE_V1_GUIDE.md
    ├── DB_INTELLIGENCE_V1_QUICK_REFERENCE.md
    ├── DB_INTELLIGENCE_V1_IMPLEMENTATION_SUMMARY.md
    ├── DB_INTELLIGENCE_V1_DEPLOYMENT.md
    ├── DB_INTELLIGENCE_V1_COMPLETE.md
    └── DB_INTELLIGENCE_V1_ARCHITECTURE.md (this file)
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| V1.0 | 2024 | Initial hybrid intelligence release |
| V3.0 | 2024 | Previous strict SQL-only version |

---

**DB-INTELLIGENCE-V1 Architecture**  
*Where Data Meets Intelligence*
