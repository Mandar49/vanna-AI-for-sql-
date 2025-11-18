# AI Analyst System Flow Diagram

## Complete Request Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER QUESTION                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      QUERY ROUTER                                │
│  - Classify query type                                           │
│  - Detect person queries                                         │
│  - Route to appropriate handler                                  │
└────────────┬────────────────┬────────────────┬───────────────────┘
             │                │                │
    ┌────────▼────────┐  ┌───▼────┐  ┌───────▼────────┐
    │  PERSON QUERY   │  │  SQL   │  │    GENERAL     │
    │                 │  │  QUERY │  │     QUERY      │
    └────────┬────────┘  └───┬────┘  └───────┬────────┘
             │               │                │
             ▼               ▼                ▼
┌────────────────────┐  ┌──────────────┐  ┌──────────────┐
│  PERSON LOOKUP     │  │ SQL GENERATOR│  │  LLM BRAIN   │
│  1. Search         │  │ (Vanna)      │  │  (Mistral)   │
│     employees      │  └──────┬───────┘  └──────┬───────┘
│  2. Search         │         │                  │
│     customers      │         ▼                  │
│  3. Return result  │  ┌──────────────┐         │
└────────┬───────────┘  │ SQL CORRECTOR│         │
         │              │ - Validate   │         │
         │              │ - Execute    │         │
         │              │ - Retry      │         │
         │              └──────┬───────┘         │
         │                     │                 │
         │              ┌──────▼───────┐         │
         │              │  SQL RESULT  │         │
         │              │  (DataFrame) │         │
         │              └──────┬───────┘         │
         │                     │                 │
         │              ┌──────▼───────┐         │
         │              │ DATA         │         │
         │              │ VALIDATOR    │         │
         │              │ - Check      │         │
         │              │   numbers    │         │
         │              └──────┬───────┘         │
         │                     │                 │
         │              ┌──────▼───────┐         │
         │              │ BUSINESS     │         │
         │              │ ANALYST      │         │
         │              │ - Analyze    │         │
         │              │ - NO MATH    │         │
         │              └──────┬───────┘         │
         │                     │                 │
         │              ┌──────▼───────┐         │
         │              │ RESPONSE     │         │
         │              │ COMPOSER     │         │
         │              │ - Format     │         │
         │              │ - Persona    │         │
         │              └──────┬───────┘         │
         │                     │                 │
         └─────────────────────┴─────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FORMATTED RESPONSE                            │
│                                                                  │
│  ────────────────────────────────────────────────────────────   │
│  SQL RESULT                                                      │
│  ────────────────────────────────────────────────────────────   │
│  [Data table or error message]                                  │
│                                                                  │
│  ────────────────────────────────────────────────────────────   │
│  ANALYST                                                         │
│  ────────────────────────────────────────────────────────────   │
│  [Analysis using ONLY exact database values]                    │
│                                                                  │
│  ────────────────────────────────────────────────────────────   │
│  SQL QUERY                                                       │
│  ────────────────────────────────────────────────────────────   │
│  [SQL query executed]                                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Person Query Flow (Detailed)

```
User: "Tell me about John Doe"
         │
         ▼
┌────────────────────────┐
│  DETECT PERSON QUERY   │
│  - Keywords: "tell me  │
│    about", "who is"    │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│  EXTRACT NAME          │
│  - Parse: "John Doe"   │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│  SEARCH EMPLOYEES      │
│  SELECT * FROM         │
│  employees WHERE       │
│  FirstName='John' AND  │
│  LastName='Doe'        │
└───────────┬────────────┘
            │
      ┌─────┴─────┐
      │           │
   FOUND      NOT FOUND
      │           │
      ▼           ▼
┌──────────┐  ┌──────────────┐
│  RETURN  │  │ SEARCH       │
│  DATA    │  │ CUSTOMERS    │
└────┬─────┘  └──────┬───────┘
     │               │
     │         ┌─────┴─────┐
     │         │           │
     │      FOUND      NOT FOUND
     │         │           │
     │         ▼           ▼
     │    ┌──────────┐  ┌──────────────┐
     │    │  RETURN  │  │  RETURN      │
     │    │  DATA    │  │  "NOT FOUND" │
     │    └────┬─────┘  └──────┬───────┘
     │         │               │
     └─────────┴───────────────┘
               │
               ▼
┌──────────────────────────────┐
│  FORMAT RESPONSE             │
│  - SQL RESULT section        │
│  - Show database data OR     │
│    "does not exist" message  │
│  - NO external knowledge     │
└──────────────┬───────────────┘
               │
               ▼
         USER RESPONSE
```

---

## SQL Query Flow (Detailed)

```
User: "Show me sales by year"
         │
         ▼
┌────────────────────────┐
│  GENERATE SQL          │
│  (Vanna AI)            │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│  VALIDATE SCHEMA       │
│  - Check tables exist  │
│  - Check columns exist │
└───────────┬────────────┘
            │
      ┌─────┴─────┐
      │           │
   VALID      INVALID
      │           │
      ▼           ▼
┌──────────┐  ┌──────────────┐
│ EXECUTE  │  │ AUTO-CORRECT │
│ SQL      │  │ - Fix table  │
└────┬─────┘  │   names      │
     │        │ - Fix column │
     │        │   references │
     │        └──────┬───────┘
     │               │
     │               ▼
     │        ┌──────────────┐
     │        │ RETRY        │
     │        │ EXECUTION    │
     │        └──────┬───────┘
     │               │
     └───────────────┘
               │
         ┌─────┴─────┐
         │           │
     SUCCESS      ERROR
         │           │
         ▼           ▼
┌────────────────┐  ┌──────────────┐
│  DATAFRAME     │  │ ERROR FORMAT │
│  (Results)     │  │ - Reason     │
└───────┬────────┘  │ - Suggestion │
        │           └──────┬───────┘
        │                  │
        ▼                  │
┌────────────────┐         │
│  VALIDATE      │         │
│  NUMBERS       │         │
│  - Check all   │         │
│    numbers in  │         │
│    response    │         │
│    exist in DF │         │
└───────┬────────┘         │
        │                  │
        ▼                  │
┌────────────────┐         │
│  ANALYZE       │         │
│  (Business     │         │
│   Analyst)     │         │
│  - NO MATH     │         │
│  - EXACT DATA  │         │
└───────┬────────┘         │
        │                  │
        ▼                  │
┌────────────────┐         │
│  COMPOSE       │         │
│  RESPONSE      │         │
│  - Format      │         │
│  - Persona     │         │
└───────┬────────┘         │
        │                  │
        └──────────────────┘
                │
                ▼
┌────────────────────────────┐
│  FORMATTED RESPONSE        │
│  SQL RESULT → ANALYST →    │
│  SQL QUERY                 │
└────────────────────────────┘
```

---

## Error Handling Flow

```
SQL Execution Error
         │
         ▼
┌────────────────────────┐
│  IDENTIFY ERROR TYPE   │
│  - 1064: Syntax        │
│  - 1146: Table missing │
│  - 1054: Column missing│
│  - 2003: Connection    │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│  ATTEMPT CORRECTION    │
│  - Fix table names     │
│  - Fix column refs     │
│  - Retry connection    │
└───────────┬────────────┘
            │
      ┌─────┴─────┐
      │           │
  CORRECTED   FAILED
      │           │
      ▼           ▼
┌──────────┐  ┌──────────────┐
│  RETRY   │  │ FORMAT ERROR │
│  SQL     │  │ MESSAGE      │
└────┬─────┘  └──────┬───────┘
     │               │
     └───────────────┘
               │
               ▼
┌──────────────────────────────┐
│  ERROR RESPONSE              │
│  ────────────────────────    │
│  SQL RESULT                  │
│  ────────────────────────    │
│  ❌ SQL ERROR                │
│                              │
│  Reason: [Clean explanation] │
│                              │
│  Suggestion: [Next step]     │
│  ────────────────────────    │
│  SQL QUERY                   │
│  ────────────────────────    │
│  [Attempted query]           │
└──────────────────────────────┘
```

---

## Validation Flow

```
LLM Response Generated
         │
         ▼
┌────────────────────────┐
│  EXTRACT NUMBERS       │
│  - Parse response text │
│  - Find all numeric    │
│    values              │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│  EXTRACT DB NUMBERS    │
│  - Get all numeric     │
│    values from         │
│    DataFrame           │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│  COMPARE               │
│  - Check each response │
│    number exists in DB │
│  - Allow: years,       │
│    row counts          │
└───────────┬────────────┘
            │
      ┌─────┴─────┐
      │           │
   VALID      INVALID
      │           │
      ▼           ▼
┌──────────┐  ┌──────────────┐
│  PASS    │  │ ADD WARNING  │
│  THROUGH │  │ - List       │
└────┬─────┘  │   suspicious │
     │        │   numbers    │
     │        └──────┬───────┘
     │               │
     └───────────────┘
               │
               ▼
         FINAL RESPONSE
```

---

## CAGR Calculation Flow

```
User: "Calculate CAGR from 2023 to 2024"
         │
         ▼
┌────────────────────────┐
│  DETECT CAGR QUERY     │
│  - Keywords: "cagr",   │
│    "growth rate"       │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│  EXTRACT YEARS         │
│  - Start: 2023         │
│  - End: 2024           │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│  SQL CALCULATION       │
│  SELECT                │
│    ROUND((POWER(       │
│      end/start,        │
│      1/(end_yr-start)  │
│    ) - 1) * 100, 2)    │
│  AS CAGR               │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│  EXECUTE SQL           │
│  - Get start sales     │
│  - Get end sales       │
│  - Get CAGR            │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│  VALIDATE CAGR         │
│  - Check formula       │
│  - Verify calculation  │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│  LLM COMMENTARY        │
│  - NO MATH             │
│  - Use exact CAGR      │
│  - Qualitative only    │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│  FORMAT RESPONSE       │
│  - Show SQL RESULT     │
│  - Show CAGR value     │
│  - Show ANALYST        │
│  - Show SQL QUERY      │
└────────────────────────┘
```

---

## Key Principles Illustrated

### 1. SQL-First
```
❌ WRONG:
User Question → LLM Analysis → SQL → Results

✅ CORRECT:
User Question → SQL → Results → LLM Analysis
```

### 2. No Calculations
```
❌ WRONG:
LLM: "Sales grew by 50% (150000-100000)/100000"

✅ CORRECT:
LLM: "Sales increased from 100000 to 150000"
```

### 3. No External Knowledge
```
❌ WRONG:
LLM: "John Doe is a famous entrepreneur..."

✅ CORRECT:
LLM: "John Doe does not exist in your database"
```

### 4. Strict Format
```
✅ ALWAYS:
────────────────────────────────────────────────────────────
SQL RESULT
────────────────────────────────────────────────────────────
[data]
────────────────────────────────────────────────────────────
ANALYST
────────────────────────────────────────────────────────────
[analysis]
────────────────────────────────────────────────────────────
SQL QUERY
────────────────────────────────────────────────────────────
[sql]
```

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (Flask)                        │
│  - User interface                                            │
│  - Request handling                                          │
│  - Response rendering                                        │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                    ROUTING LAYER                             │
│  - query_router.py                                           │
│  - Classifies queries (person/sql/general)                   │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
┌────────▼────────┐ ┌───▼────┐ ┌───────▼────────┐
│  PERSON HANDLER │ │  SQL   │ │    GENERAL     │
│                 │ │ HANDLER│ │    HANDLER     │
└────────┬────────┘ └───┬────┘ └───────┬────────┘
         │              │               │
┌────────▼────────┐ ┌───▼──────────────▼────────┐
│ business_       │ │  sql_corrector.py         │
│ analyst.py      │ │  - Schema validation      │
│ - Person lookup │ │  - SQL execution          │
│ - Analysis      │ │  - Error handling         │
└────────┬────────┘ └───┬───────────────────────┘
         │              │
         │         ┌────▼────────┐
         │         │ DATABASE    │
         │         │ (MySQL)     │
         │         └────┬────────┘
         │              │
         └──────────────┘
                  │
         ┌────────▼────────┐
         │ data_validator  │
         │ - Number check  │
         │ - Validation    │
         └────────┬────────┘
                  │
         ┌────────▼────────┐
         │ response_       │
         │ composer.py     │
         │ - Formatting    │
         │ - Personas      │
         └────────┬────────┘
                  │
                  ▼
            USER RESPONSE
```

---

**This diagram shows the complete flow of the AI Analyst system with all PRIMARY RULES enforced.**
