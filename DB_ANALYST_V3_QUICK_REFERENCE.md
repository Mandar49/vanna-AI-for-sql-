# DB-ANALYST-V3 QUICK REFERENCE

## 🎯 What is DB-ANALYST-V3?

DB-ANALYST-V3 is a STRICT database-only AI analyst that:
- ✅ ONLY answers questions using your database
- ✅ NEVER invents or calculates numbers
- ✅ NEVER uses external knowledge (no Wikipedia, no world facts)
- ✅ ALWAYS shows SQL query used
- ✅ ALWAYS follows strict output format

---

## 📋 THE 5 RULES

### Rule 1: SQL First - ALWAYS
**Every question MUST:**
1. Generate SQL
2. Execute SQL
3. Get results (or error)
4. THEN analyze

**NO exceptions.** Even "strategic" questions go through SQL first.

### Rule 2: No Hallucination
**The LLM can ONLY:**
- ✅ Restate exact numbers from SQL RESULT
- ✅ Compare values (e.g., "A is higher than B")
- ✅ Identify patterns using exact values

**The LLM CANNOT:**
- ❌ Calculate percentages
- ❌ Calculate growth rates
- ❌ Calculate averages (unless in SQL)
- ❌ Derive any new numbers

### Rule 3: Strict Output Format
**Success format:**
```
SQL RESULT
[table with data]

ANALYST
[analysis using ONLY exact values from SQL RESULT]

SQL QUERY
[exact SQL that was executed]
```

**Error format:**
```
SQL RESULT
❌ SQL ERROR / NO DATA FOUND / DATABASE LIMITATION
Reason: [clear explanation]
Suggestion: [helpful next step]

SQL QUERY
[SQL that failed]
```

### Rule 4: Database-Only Values
**Every number in ANALYST section MUST:**
- Appear EXACTLY in SQL RESULT (within 0.001 tolerance)
- Come from the database, not calculations
- Be validated by `data_validator.py`

**If a number doesn't exist in SQL RESULT → INVALID**

### Rule 5: Correct SQL
**SQL errors must:**
- Have clean, human-readable messages
- Provide helpful suggestions
- Follow strict error format
- NO stack traces, NO technical jargon

---

## 🧪 HOW TO TEST

### Run Full Test Suite
```bash
python test_db_analyst_v3.py
```

Expected: **33/33 tests passing (100%)**

### Quick Manual Tests

#### Test 1: Person Not in Database
```
Ask: "Tell me about Shah Rukh Khan"
Expected: "Shah Rukh Khan does not exist in your database"
Should NOT: Provide Bollywood biography
```

#### Test 2: Missing Column
```
Ask: "Show me units_sold from salesorders"
Expected: Clean SQL ERROR with reason and suggestion
Should NOT: Hallucinate data or show stack trace
```

#### Test 3: CAGR Calculation
```
Ask: "What is the CAGR from 2023 to 2024?"
Expected: CAGR calculated directly from SQL
Should NOT: LLM calculate percentage
```

#### Test 4: General Knowledge
```
Ask: "What is Bollywood?"
Expected: "This system only answers questions about your database"
Should NOT: Provide general knowledge answer
```

---

## 🔍 WHERE RULES ARE ENFORCED

### SQL-First Guarantee
- **File:** `ad_ai_app.py` line 820
- **What:** Removed strategic analyst brain
- **Result:** ALL questions go through SQL first

### No Hallucination
- **Files:** `business_analyst.py`, `response_composer.py`
- **What:** LLM prompts enforce "NO CALCULATIONS"
- **Result:** LLM can only restate exact values

### Strict Output Format
- **File:** `ad_ai_app.py` lines 900-1000
- **What:** Format enforcement in response generation
- **Result:** Always SQL RESULT → ANALYST → SQL QUERY

### Database-Only Values
- **File:** `data_validator.py` lines 50-100
- **What:** Strict validation (tolerance 0.001)
- **Result:** Catches any fabricated numbers

### Correct SQL
- **File:** `sql_corrector.py` lines 500-700
- **What:** Enhanced error handling
- **Result:** Clean error messages with suggestions

---

## 🚨 COMMON VIOLATIONS (NOW BLOCKED)

### ❌ VIOLATION: LLM Calculates Percentage
**Before:**
```
"Sales grew by 50% from 100,000 to 150,000"
```
**After (DB-ANALYST-V3):**
```
"Sales increased from 100,000 to 150,000"
```
**Why:** 50% is a calculation, not in SQL RESULT

### ❌ VIOLATION: External Knowledge
**Before:**
```
"Shah Rukh Khan is a famous Bollywood actor..."
```
**After (DB-ANALYST-V3):**
```
"Shah Rukh Khan does not exist in your database"
```
**Why:** Bollywood info is external knowledge

### ❌ VIOLATION: Bypassing SQL
**Before:**
```
Strategic question → LLM generates answer directly
```
**After (DB-ANALYST-V3):**
```
Strategic question → Generate SQL → Execute → Analyze
```
**Why:** SQL-first is mandatory

### ❌ VIOLATION: Messy Error
**Before:**
```
"Error: mysql.connector.errors.ProgrammingError: 1054 (42S22): Unknown column..."
```
**After (DB-ANALYST-V3):**
```
SQL RESULT
❌ SQL ERROR
Reason: Column 'units_sold' does not exist in any table
Suggestion: Try asking 'What columns does table X have?'
```
**Why:** Clean, helpful error format

---

## 📊 VALIDATION CHECKLIST

Use this checklist to verify DB-ANALYST-V3 compliance:

- [ ] **SQL First:** Did the system generate and execute SQL before analyzing?
- [ ] **No Calculations:** Are all numbers in ANALYST section from SQL RESULT?
- [ ] **No External Knowledge:** Did the system search database before answering about people/entities?
- [ ] **Strict Format:** Does response follow SQL RESULT → ANALYST → SQL QUERY?
- [ ] **Clean Errors:** Are error messages clear with reason and suggestion?
- [ ] **Exact Values:** Can you find every number in ANALYST within SQL RESULT?

**If ANY checkbox is unchecked → VIOLATION**

---

## 🔧 TROUBLESHOOTING

### Problem: LLM is calculating percentages
**Solution:** Check `business_analyst.py` and `response_composer.py` prompts. They must contain:
```
"EVERY NUMBER YOU MENTION MUST APPEAR EXACTLY IN SQL RESULT"
```

### Problem: External knowledge appearing
**Solution:** Check `query_router.py`. General queries should be blocked:
```python
return {
    "type": "general",
    "answer": "This system only answers questions about your database..."
}
```

### Problem: Strategic brain bypassing SQL
**Solution:** Check `ad_ai_app.py` line 820. Strategic analyst brain should be removed:
```python
# DB-ANALYST-V3: Remove strategic analyst brain - ALL questions must go through SQL first
```

### Problem: Validation not catching fabricated numbers
**Solution:** Check `data_validator.py` tolerance. Should be 0.001:
```python
def validate_response(self, response: str, df: pd.DataFrame, tolerance: float = 0.001)
```

---

## 📈 SUCCESS METRICS

### Test Results
- **Target:** 100% tests passing
- **Current:** 33/33 passing (100%)
- **Status:** ✅ COMPLIANT

### Key Indicators
- ✅ No calculated percentages in responses
- ✅ No external knowledge (Bollywood, actors, etc.)
- ✅ All responses follow strict format
- ✅ Clean error messages with suggestions
- ✅ CAGR comes from SQL, not LLM

---

## 🎓 FOR DEVELOPERS

### Adding New Features
1. **Always enforce SQL-first:** Generate SQL before analysis
2. **Never allow calculations:** LLM restates exact values only
3. **Maintain strict format:** SQL RESULT → ANALYST → SQL QUERY
4. **Validate responses:** Use `validator.validate_response()`
5. **Add tests:** Update `test_db_analyst_v3.py`

### Modifying LLM Prompts
**CRITICAL:** All LLM prompts MUST include:
```
🔐 DB-ANALYST-V3 ABSOLUTE RULES (VIOLATION = FAILURE):
1. You are DB-ANALYST-V3, operating STRICTLY on the user's private business database
2. ALL analysis MUST use ONLY exact numbers from SQL RESULT below
3. ❌ NEVER calculate, compute, or derive ANY values
4. ❌ NEVER use external knowledge
5. ✔ ONLY copy exact numbers from SQL RESULT verbatim
```

### Testing Changes
```bash
# Run full test suite
python test_db_analyst_v3.py

# Expected output
✓ Passed: 33
✗ Failed: 0
Success Rate: 100.0%
```

---

## 📞 SUPPORT

### If Tests Fail
1. Check which rule is violated (see test output)
2. Review the relevant file (see "WHERE RULES ARE ENFORCED")
3. Verify prompts contain DB-ANALYST-V3 rules
4. Check validation tolerance (should be 0.001)
5. Run tests again

### If Behavior is Unexpected
1. Check `ad_ai_app.py` for strategic brain (should be removed)
2. Check `query_router.py` for general query handling
3. Check `business_analyst.py` for calculation logic (should be removed)
4. Check `data_validator.py` for validation strictness

---

**Version:** DB-ANALYST-V3  
**Status:** ✅ PRODUCTION READY  
**Test Coverage:** 100%  
**Last Updated:** 2025-11-17
