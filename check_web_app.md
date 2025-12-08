# Check These Things on PythonAnywhere

## 1. Check WSGI Error Log

After updating the WSGI file, check for errors:

```bash
cat /home/3pillars/wsgi_error.log
```

## 2. Test WSGI Directly

```bash
cd ~/threepillars
python3.12 test_wsgi_direct.py
```

This will show if WSGI works when called directly.

## 3. Check Web App Configuration

In "Web" tab, verify:

- **Source code:** `/home/3pillars/threepillars`
- **Working directory:** `/home/3pillars/threepillars` (or leave blank)
- **Virtualenv:** `/home/3pillars/venv` (check with `which python3.12`)
- **WSGI file:** `/var/www/3pillars_pythonanywhere_com_wsgi.py`

## 4. Check PythonAnywhere Error Log

In "Web" tab:
- Scroll down to "Error log" section
- Copy the latest errors
- Look for tracebacks

## 5. Check if Web App is Actually Running

```bash
# Check if there's a process running
ps aux | grep python | grep wsgi
```

## 6. Try Manual WSGI Test

```bash
cd ~/threepillars
python3.12 -c "
import sys
sys.path.insert(0, '/home/3pillars/threepillars')
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'webcrm.settings'
from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
print('WSGI app created:', type(app))
"
```

If this works but web app doesn't, it's a PythonAnywhere configuration issue.

## 7. Check Virtualenv

Make sure virtualenv path in web app matches:

```bash
which python3.12
# Should show: /home/3pillars/venv/bin/python3.12
# So virtualenv in web app should be: /home/3pillars/venv
```

## 8. Force Reload

After making changes:
1. Go to "Web" tab
2. Click "Reload" button
3. Wait 30 seconds
4. Try accessing the site

## 9. Check for Timeout

If requests timeout, check:
- Database connection (might be slow)
- Any middleware that runs on startup
- Import statements that do heavy work

Run `test_wsgi_direct.py` - it will show exactly where it fails.

