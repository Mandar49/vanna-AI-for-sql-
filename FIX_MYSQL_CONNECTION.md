# Fix MySQL Connection Error

## Error
```
ConnectionRefusedError: [WinError 10061] No connection could be made because the target machine actively refused it
InterfaceError: 2003: Can't connect to MySQL server on 'localhost:3306'
```

## Cause
MySQL server is not running on your Windows machine.

## Solution

### Step 1: Start MySQL Service

**Option A: Using Services (Recommended)**
1. Press `Win + R`
2. Type `services.msc` and press Enter
3. Scroll down to find "MySQL" or "MySQL80"
4. Right-click on it → Click "Start"
5. Right-click again → Properties → Set "Startup type" to "Automatic"

**Option B: Using Command Prompt (Run as Administrator)**
```cmd
net start MySQL80
```

**Option C: Using MySQL Workbench**
1. Open MySQL Workbench
2. Click "Server" → "Startup / Shutdown"
3. Click "Start Server"

### Step 2: Verify MySQL is Running

Test the connection:
```cmd
mysql -u root -p
```
Press Enter when prompted for password (your password is empty).

If you see `mysql>` prompt, MySQL is running correctly.

### Step 3: Run Training Again

```cmd
python train.py
```

## If MySQL is Not Installed

Download and install MySQL Community Server:
https://dev.mysql.com/downloads/mysql/

During installation:
- Set root password (or leave empty to match your config)
- Enable "Start MySQL Server at System Startup"

## Current Connection Settings

Your `common.py` has these settings:
```python
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''  # Empty password
DB_NAME = 'ad_ai_testdb'
```

If your MySQL uses different settings, update these values in `common.py`.

## Troubleshooting

### Check if MySQL is listening on port 3306:
```cmd
netstat -ano | findstr :3306
```

### Check MySQL service status:
```cmd
sc query MySQL80
```

### View MySQL error log:
Check: `C:\ProgramData\MySQL\MySQL Server 8.0\Data\*.err`

## Common Issues

1. **Service name is different**: Try `MySQL`, `MySQL57`, `MySQL80`, etc.
2. **Port conflict**: Another service is using port 3306
3. **Firewall**: Windows Firewall is blocking MySQL
4. **Wrong credentials**: Username or password is incorrect

## Need Help?

If MySQL still won't start, check the MySQL error log for specific issues.
