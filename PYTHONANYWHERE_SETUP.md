# PythonAnywhere Web App Configuration

Since Django works when run manually, the issue is your **Web app configuration** on PythonAnywhere.

## Check Your Web App Settings:

1. **Go to "Web" tab** on PythonAnywhere
2. **Click on your web app** (3pillars.pythonanywhere.com)
3. **Verify these settings:**

### Source Code:
- **Source code:** `/home/3pillars/threepillars`

### WSGI Configuration File:
- **Path:** `/home/3pillars/threepillars/webcrm/wsgi.py`
- **Or:** `/var/www/3pillars_pythonanywhere_com_wsgi.py` (if using the default)

### Virtualenv:
- **Path:** `/home/3pillars/.virtualenvs/venv`
- **Or:** `/home/3pillars/venv`
- **Make sure this matches where your venv actually is!**

### Python Version:
- Should be **Python 3.12** (or whatever version you're using)

## Common Issues:

### 1. Wrong WSGI File Path
The WSGI file path in PythonAnywhere web app config must be:
```
/home/3pillars/threepillars/webcrm/wsgi.py
```

### 2. Virtualenv Not Set
If virtualenv path is wrong, Django won't find installed packages.

Check where your venv is:
```bash
which python3.12
# Should show: /home/3pillars/venv/bin/python3.12
# Or: /home/3pillars/.virtualenvs/venv/bin/python3.12
```

### 3. Web App Not Reloaded
After changing code, you **MUST** click "Reload" button in Web tab.

### 4. WSGI File Content
The WSGI file should have:
```python
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webcrm.settings')

application = get_wsgi_application()
```

## Test WSGI:

Run this to test if WSGI works:
```bash
cd ~/threepillars
python3.12 check_wsgi.py
```

If that works but web app still 502s, the issue is the **web app configuration**, not your code.

## Fix Steps:

1. **Check WSGI file path** in web app config
2. **Check virtualenv path** - must be exact
3. **Click "Reload"** button
4. **Check error log** in web app (scroll down in Web tab)

The error log in the Web tab will show the actual WSGI error if there is one.

