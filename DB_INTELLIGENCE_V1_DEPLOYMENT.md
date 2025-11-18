# DB-INTELLIGENCE-V1 Deployment Guide

## Pre-Deployment Checklist

### ✅ Verification Steps

1. **Run Tests**
```bash
python test_hybrid_intelligence.py
```
Expected: All 9 tests passing ✓

2. **Check Dependencies**
```bash
pip list | grep -E "pandas|flask|ollama|mysql"
```
All existing dependencies are sufficient - no new packages required.

3. **Backup Current System**
```bash
# Backup main application
cp ad_ai_app.py ad_ai_app_v3_backup.py

# Backup modified files
cp query_router.py query_router_v3_backup.py
cp business_analyst.py business_analyst_v3_backup.py
cp response_composer.py response_composer_v3_backup.py
```

## Deployment Options

### Option 1: Quick Deployment (Recommended)

**Step 1**: Rename hybrid app to main app
```bash
mv ad_ai_app.py ad_ai_app_v3.py
mv ad_ai_app_hybrid.py ad_ai_app.py
```

**Step 2**: Restart server
```bash
python ad_ai_app.py
```

**Step 3**: Verify
```bash
curl -X POST http://localhost:5000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is customer churn?", "conversation_id": "test_123"}'
```

### Option 2: Gradual Migration

**Step 1**: Run hybrid app on different port
```python
# In ad_ai_app_hybrid.py, change last line:
app.run(debug=True, host='0.0.0.0', port=5001)
```

**Step 2**: Test on port 5001
```bash
python ad_ai_app_hybrid.py
```

**Step 3**: Compare outputs between ports 5000 and 5001

**Step 4**: Switch when confident
```bash
# Stop old server (port 5000)
# Rename files as in Option 1
# Start new server on port 5000
```

### Option 3: Docker Deployment

**Step 1**: Create Dockerfile
```dockerfile
FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Use hybrid app
RUN mv ad_ai_app_hybrid.py ad_ai_app.py

EXPOSE 5000

CMD ["python", "ad_ai_app.py"]
```

**Step 2**: Build and run
```bash
docker build -t db-intelligence-v1 .
docker run -p 5000:5000 db-intelligence-v1
```

## Post-Deployment Verification

### Test Suite

Run these queries to verify all functionality:

#### 1. SQL Query Test
```json
{
  "question": "Show me total sales by year",
  "conversation_id": "test_sql",
  "mode": "DETAILED"
}
```

**Expected Output**:
- SQL RESULT section with data
- INSIGHT section with interpretation
- STRATEGIC RECOMMENDATION section
- SQL QUERY EXECUTED section

#### 2. Empty Result Test
```json
{
  "question": "Show me customers in Antarctica",
  "conversation_id": "test_empty",
  "mode": "DETAILED"
}
```

**Expected Output**:
- SQL RESULT: "No data found"
- INSIGHT: Reasoning about why
- STRATEGIC RECOMMENDATION: Next steps

#### 3. General Knowledge Test
```json
{
  "question": "What is customer churn?",
  "conversation_id": "test_general",
  "mode": "DETAILED"
}
```

**Expected Output**:
- ANSWER section with definition
- No SQL query

#### 4. Person Query Test
```json
{
  "question": "Tell me about John Smith",
  "conversation_id": "test_person",
  "mode": "DETAILED"
}
```

**Expected Output**:
- SQL RESULT with person data or "not found"
- INSIGHT about the person
- STRATEGIC RECOMMENDATION if not found

### Performance Monitoring

**Monitor these metrics**:

1. **Response Time**
```bash
# Should be similar to V3 + 50-100ms
time curl -X POST http://localhost:5000/api/ask -H "Content-Type: application/json" -d '{"question": "Show me all customers", "conversation_id": "perf_test"}'
```

2. **Memory Usage**
```bash
# Should be V3 memory + ~10MB
ps aux | grep python
```

3. **Error Rate**
```bash
# Check error logs
tail -f logs/error.log
```

### Rollback Plan

If issues occur:

**Quick Rollback**:
```bash
# Stop current server
# Restore backup
mv ad_ai_app_v3_backup.py ad_ai_app.py
mv query_router_v3_backup.py query_router.py
mv business_analyst_v3_backup.py business_analyst.py
mv response_composer_v3_backup.py response_composer.py

# Restart server
python ad_ai_app.py
```

## Configuration

### Response Mode

Set default mode in `ad_ai_app.py`:
```python
# For more concise responses
composer.set_mode('COMPACT')

# For detailed analysis (default)
composer.set_mode('DETAILED')
```

### Framework Customization

Edit `hybrid_reasoner.py` to add custom frameworks:

```python
def _custom_framework(self, result, question):
    """Your custom business framework"""
    return "Your custom insight logic here"

# Add to frameworks dict in __init__
self.frameworks['custom'] = self._custom_framework
```

### Keyword Tuning

Adjust SQL detection in `hybrid_reasoner.py`:

```python
def should_use_sql(self, question):
    sql_indicators = [
        # Add your custom keywords
        'metric', 'kpi', 'dashboard'
    ]
```

## Monitoring Dashboard

### Key Metrics to Track

1. **Query Distribution**
   - SQL queries: X%
   - General questions: Y%
   - Person queries: Z%

2. **Empty Result Rate**
   - Track how often SQL returns no data
   - Monitor if recommendations are helpful

3. **Framework Usage**
   - Which frameworks are most used
   - Framework detection accuracy

4. **User Satisfaction**
   - Response quality ratings
   - Follow-up question patterns

### Logging

Enhanced logging is built-in:

```python
# Check logs
tail -f logs/query.log
tail -f logs/error.log
tail -f logs/reasoning.log  # New in V1
```

## Troubleshooting

### Issue: "Module not found: hybrid_reasoner"

**Solution**:
```bash
# Ensure hybrid_reasoner.py is in the same directory
ls -la hybrid_reasoner.py

# Check Python path
python -c "import sys; print(sys.path)"
```

### Issue: Tests pass but app fails

**Solution**:
```bash
# Check imports in ad_ai_app.py
python -c "from hybrid_reasoner import HybridReasoner; print('OK')"

# Verify all files are present
ls -la hybrid_reasoner.py ad_ai_app_hybrid.py
```

### Issue: Responses still say "out of scope"

**Solution**:
```bash
# Verify you're running the hybrid version
grep "DB-INTELLIGENCE-V1" ad_ai_app.py

# Check query_router.py was updated
grep "hybrid_reasoner" query_router.py
```

### Issue: No strategic recommendations

**Solution**:
```python
# Test hybrid reasoner directly
python -c "
from hybrid_reasoner import HybridReasoner
r = HybridReasoner()
result = r._suggest_next_action('customer retention', {})
print(result)
"
```

### Issue: Performance degradation

**Solution**:
1. Check if Ollama is running: `ollama list`
2. Monitor database connections
3. Review query complexity
4. Consider caching recommendations

## Production Best Practices

### 1. Environment Variables

```bash
# Set in production
export DB_INTELLIGENCE_MODE=COMPACT  # or DETAILED
export ENABLE_HYBRID_REASONING=true
export LOG_LEVEL=INFO
```

### 2. Rate Limiting

Add rate limiting for reasoning layer:
```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=get_remote_address)

@app.route('/api/ask')
@limiter.limit("10 per minute")
def ask():
    # ...
```

### 3. Caching

Cache framework recommendations:
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_framework_insight(framework_name, question_hash):
    # Cache framework responses
    pass
```

### 4. Monitoring

Set up alerts:
```python
# Alert if error rate > 5%
# Alert if response time > 2s
# Alert if empty result rate > 50%
```

## Success Criteria

Deployment is successful when:

- ✅ All 9 tests passing
- ✅ SQL queries return accurate data
- ✅ Empty results provide insights
- ✅ General questions answered
- ✅ Response time < 2 seconds
- ✅ Error rate < 1%
- ✅ No "out of scope" messages
- ✅ User satisfaction improved

## Support

### Documentation
- `DB_INTELLIGENCE_V1_GUIDE.md` - Complete guide
- `DB_INTELLIGENCE_V1_QUICK_REFERENCE.md` - Quick reference
- `DB_INTELLIGENCE_V1_IMPLEMENTATION_SUMMARY.md` - Technical details

### Testing
- `test_hybrid_intelligence.py` - Run full test suite
- Individual component tests available

### Logs
- `logs/error.log` - Error tracking
- `logs/query.log` - Query history
- `logs/reasoning.log` - Reasoning decisions

---

## Quick Start Commands

```bash
# 1. Backup
cp ad_ai_app.py ad_ai_app_v3_backup.py

# 2. Deploy
mv ad_ai_app_hybrid.py ad_ai_app.py

# 3. Test
python test_hybrid_intelligence.py

# 4. Start
python ad_ai_app.py

# 5. Verify
curl -X POST http://localhost:5000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is customer churn?", "conversation_id": "test"}'
```

**Status**: Ready for deployment ✅

**Version**: DB-INTELLIGENCE-V1

**Date**: 2024
