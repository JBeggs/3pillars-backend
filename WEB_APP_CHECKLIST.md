# PythonAnywhere Web App Configuration Checklist

Since `minimal_wsgi_test.py` passes, your code is fine. The issue is web app config.

## ✅ Verify These Settings in Web Tab:

### 1. Source Code
- **Path:** `/home/3pillars/threepillars`

### 2. Working Directory  
- **Path:** `/home/3pillars/threepillars` (or leave blank)

### 3. Virtualenv
- **Path:** `/home/3pillars/venv` (exactly this, no trailing slash)
- Verify with: `which python3.12` should show `/home/3pillars/venv/bin/python3.12`

### 4. WSGI Configuration File
- **Path:** `/var/www/3pillars_pythonanywhere_com_wsgi.py`
- **Content should be:**
```python
import os
import sys

project_home = '/home/3pillars/threepillars'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['DJANGO_SETTINGS_MODULE'] = 'webcrm.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 5. Python Version
- Should match your venv Python version (3.12)

## 🔧 Steps to Fix:

1. **Verify virtualenv path:**
   ```bash
   which python3.12
   # Should show: /home/3pillars/venv/bin/python3.12
   # So virtualenv in web app = /home/3pillars/venv
   ```

2. **Update WSGI file** (if needed):
   - Go to Files tab
   - Edit `/var/www/3pillars_pythonanywhere_com_wsgi.py`
   - Make sure it matches the content above

3. **Click "Reload"** in Web tab

4. **Wait 30 seconds** for reload to complete

5. **Check error log** in Web tab (scroll down)

## 🐛 If Still 502:

Check the **Error log** section in Web tab (scroll down). It will show:
- Import errors
- Syntax errors  
- Missing modules
- Database connection errors

The error log is the key - it will tell you exactly what's wrong.

## ⚠️ Common Issues:

1. **Virtualenv path wrong** - Most common! Must be exact: `/home/3pillars/venv`
2. **WSGI file not saved** - Make sure you saved after editing
3. **Didn't reload** - Must click "Reload" button
4. **Python version mismatch** - Web app Python ≠ venv Python

Since your code works manually, it's 100% a configuration issue in the Web tab.

