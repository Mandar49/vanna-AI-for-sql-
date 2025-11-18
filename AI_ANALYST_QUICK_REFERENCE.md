# AI Analyst System - Quick Reference Guide

## 🔐 PRIMARY RULES (ALWAYS FOLLOW)

### 1. SQL-First Execution
- ✅ **ALWAYS** execute SQL before any analysis
- ✅ Show SQL RESULT first, then ANALYST, then SQL QUERY
- ❌ **NEVER** provide analysis before SQL execution

### 2. No Hallucinations
- ✅ Use **ONLY** exact numbers from database
- ❌ **NEVER** calculate, compute, or derive values
- ❌ **NEVER** invent percentages, differences, or averages
- ❌ **NEVER** assume or fabricate ANY numerical values

### 3. No External Knowledge
- ✅ For person queries: Search database **FIRST**
- ✅ If not found: Say "does not exist in your database"
- ❌ **NEVER** use world knowledge about people/companies
- ❌ **NEVER** provide biographical info not in database

### 4. Strict Output Format
```
────────────────────────────────────────────────────────────
SQL RESULT
────────────────────────────────────────────────────────────
[Pretty table if data exists OR error message]

────────────────────────────────────────────────────────────
ANALYST
────────────────────────────────────────────────────────────
[Analysis using ONLY exact numbers from SQL RESULT]

────────────────────────────────────────────────────────────
SQL QUERY
────────────────────────────────────────────────────────────
[The SQL query that was executed]
```

### 5. Error Format
```
────────────────────────────────────────────────────────────
SQL RESULT
────────────────────────────────────────────────────────────
❌ NO DATA FOUND / SQL ERROR

Reason: [Clean explanation, no stack trace]

Suggestion: [Helpful next step]

────────────────────────────────────────────────────────────
SQL QUERY
────────────────────────────────────────────────────────────
[The SQL query that was attempted]
```

## 📋 RESPONSE CHECKLIST

Before sending any response, verify:

- [ ] SQL was executed first
- [ ] SQL RESULT section shows actual data
- [ ] ANALYST section uses ONLY exact numbers from SQL RESULT
- [ ] No calculations performed by LLM
- [ ] No external knowledge used
- [ ] SQL QUERY section shows the query
- [ ] Format matches exactly (separators, headers)
- [ ] Error messages include Reason and Suggestion

## 🚫 FORBIDDEN ACTIONS

### Never Do This:
```python
# ❌ BAD: LLM calculating growth
"The sales grew by 50% from 100000 to 150000"

# ❌ BAD: Fabricated average
"The average order value is $125.50"

# ❌ BAD: External knowledge
"John Doe is a famous entrepreneur who..."

# ❌ BAD: Assumed data
"Based on industry trends, we can expect..."
```

### Always Do This:
```python
# ✅ GOOD: Exact numbers only
"The data shows sales of 100000 in 2023 and 150000 in 2024"

# ✅ GOOD: Descriptive comparison
"Sales increased from 2023 to 2024"

# ✅ GOOD: Database lookup
"John Doe does not exist in your database"

# ✅ GOOD: Data-based observation
"Based on the data shown, Customer A has higher revenue than Customer B"
```

## 🔍 PERSON QUERY HANDLING

### Detection
Person queries contain:
- "Tell me about [name]"
- "Who is [name]"
- "What company does [name] work for"
- "Phone number of [name]"

### Flow
1. **Detect** person query
2. **Search** employees table (FirstName, LastName)
3. **Search** customers table (ContactPerson)
4. **If found**: Show database data
5. **If not found**: Return "does not exist in your database"
6. **Never** use external knowledge

### Example Response (Not Found)
```
────────────────────────────────────────────────────────────
SQL RESULT
────────────────────────────────────────────────────────────
❌ NO MATCH FOUND

Reason: Simran Ansari does not exist in your database.

Suggestion: This person is not in the employees or customers
tables. Please verify the name or add them to the database.
────────────────────────────────────────────────────────────
```

## 📊 CAGR & FORECAST HANDLING

### CAGR Calculation
- ✅ Calculated by **SQL** (corrector.calculate_cagr_sql)
- ✅ LLM provides **commentary only**
- ❌ LLM **NEVER** calculates CAGR
- ❌ LLM **NEVER** performs math

### Forecast Generation
- ✅ Calculated by **SQL** using database CAGR
- ✅ Shows base, optimistic, pessimistic scenarios
- ❌ LLM **NEVER** generates forecasts
- ❌ LLM **NEVER** predicts future values

## 🛠️ DEVELOPER GUIDELINES

### Adding New Features
When adding new features, ensure:
1. SQL executes before any analysis
2. LLM prompts include "NO CALCULATIONS" rule
3. Responses follow strict format
4. Validation catches fabricated numbers
5. Error handling includes Reason and Suggestion

### Modifying LLM Prompts
Always include these rules in prompts:
```python
"""
🔐 PRIMARY RULES:
1. Use ONLY exact numbers from data provided
2. ❌ NEVER calculate, compute, or derive values
3. ❌ NEVER use external knowledge
4. ✔ ONLY describe what you see using exact numbers
"""
```

### Testing Changes
Run the test suite:
```bash
python test_ai_analyst_rules.py
```

Verify:
- [ ] All tests pass
- [ ] No syntax errors
- [ ] Format matches exactly
- [ ] No hallucinations detected

## 📁 KEY FILES

### Core Logic
- `ad_ai_app.py`: Main Flask app, routing, response formatting
- `business_analyst.py`: LLM analysis, person lookup
- `sql_corrector.py`: SQL execution, error handling
- `response_composer.py`: Response generation with personas

### Validation & Routing
- `data_validator.py`: Number validation, hallucination detection
- `query_router.py`: Query classification, person detection

### Testing
- `test_ai_analyst_rules.py`: Comprehensive test suite

## 🎯 COMMON SCENARIOS

### Scenario 1: User asks for sales data
1. Generate SQL
2. Execute SQL
3. Show SQL RESULT (data table)
4. Show ANALYST (using exact numbers)
5. Show SQL QUERY

### Scenario 2: Query returns no data
1. Execute SQL
2. Detect empty result
3. Show SQL RESULT with ❌ NO DATA FOUND
4. Show Reason and Suggestion
5. Show SQL QUERY

### Scenario 3: User asks about a person
1. Detect person query
2. Search employees table
3. Search customers table
4. If found: Show database data
5. If not found: Show NO MATCH FOUND

### Scenario 4: SQL error occurs
1. Attempt SQL execution
2. Catch error
3. Show SQL RESULT with ❌ SQL ERROR
4. Show Reason (clean, no stack trace)
5. Show Suggestion (helpful next step)
6. Show SQL QUERY (attempted)

## 🔄 VALIDATION FLOW

```
User Question
     ↓
Generate SQL
     ↓
Execute SQL → [Success] → Show SQL RESULT
     ↓                         ↓
  [Error]              Validate Data
     ↓                         ↓
Show Error Format      Generate Analysis
     ↓                         ↓
  STOP                 Validate Numbers
                              ↓
                       Show ANALYST
                              ↓
                       Show SQL QUERY
```

## 📞 SUPPORT

### If you encounter issues:
1. Check test suite: `python test_ai_analyst_rules.py`
2. Verify format matches examples
3. Check diagnostics: `getDiagnostics()`
4. Review AI_ANALYST_RULES_IMPLEMENTATION.md

### Common Issues:
- **Hallucinated numbers**: Check LLM prompts include "NO CALCULATIONS"
- **Wrong format**: Verify separator lines and section headers
- **External knowledge**: Ensure person lookup is enabled
- **Missing validation**: Check data_validator.py is called

## ✅ FINAL CHECKLIST

Before deploying:
- [ ] All tests pass
- [ ] No syntax errors
- [ ] Format matches exactly
- [ ] Person lookup works
- [ ] Error handling correct
- [ ] No hallucinations detected
- [ ] SQL executes first
- [ ] Validation enabled

---

**Remember**: The AI Analyst operates **STRICTLY** on the user's private business database. Never guess, never hallucinate, never use outside knowledge.
