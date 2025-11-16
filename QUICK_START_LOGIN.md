# Quick Start - Login System

## Start the Server
```bash
python ad_ai_app.py
```

## Test the Fix
```bash
# Quick verification (in another terminal)
python verify_login_fix.py
```

## Access the Dashboard
1. Open browser: `http://localhost:5000/dashboard/`
2. Login with:
   - **Username**: admin
   - **Password**: admin123
3. Click "Login"
4. ✅ No more "Unexpected token" errors!

## API Endpoints

### POST /login
```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### POST /api/login
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

Both return JSON:
```json
{
  "success": true,
  "message": "Authentication successful",
  "token": "...",
  "user": {"username": "admin", "role": "admin"}
}
```

## Check Logs
```bash
# View authentication logs
cat reports/logs/auth.log

# Or on Windows
type reports\logs\auth.log
```

## Troubleshooting

### Server not responding?
```bash
# Check if server is running
curl http://localhost:5000/

# Restart server
# Press Ctrl+C to stop, then run again:
python ad_ai_app.py
```

### Still getting errors?
```bash
# Run full test suite
python test_login_fix.py

# Check diagnostics
python -c "import ad_ai_app; print('Routes:', [str(r) for r in ad_ai_app.app.url_map.iter_rules() if 'login' in str(r)])"
```

## What's Fixed?

✅ Login endpoints return JSON (not HTML)  
✅ No more "Unexpected token '<'" errors  
✅ Proper HTTP status codes (200, 401, 400)  
✅ Authentication logging to `reports/logs/auth.log`  
✅ Dashboard frontend works correctly  
✅ Both `/login` and `/api/login` work  

---

**Status**: ✅ Login API fixed — JSON mode operational and frontend now works.
