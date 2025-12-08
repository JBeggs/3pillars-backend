# How to Find the Exact Error on PythonAnywhere

## Step 1: Run the diagnostic script

```bash
cd ~/threepillars
python3.12 find_error.py
```

This will show you:
- The actual error from the error log
- What's failing during Django startup
- Database connection issues
- Import errors

## Step 2: Check error log directly

```bash
# View last 100 lines of error log
tail -100 ~/logs/error.log

# Or search for recent errors
grep -i error ~/logs/error.log | tail -20
```

## Step 3: Check web app error log

On PythonAnywhere:
1. Go to "Web" tab
2. Click on your web app
3. Scroll down to "Error log" section
4. Copy the latest errors

## Step 4: Test Django startup manually

```bash
cd ~/threepillars
python3.12 manage.py check
```

This will show configuration errors.

## Common Issues:

1. **ImportError** - Missing module or syntax error
2. **Database connection timeout** - MySQL not accessible
3. **Settings error** - Syntax error in settings.py
4. **Missing dependency** - Package not installed

Run `find_error.py` first - it will tell you exactly what's wrong.

