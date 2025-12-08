# This file contains the WSGI configuration required to serve up your
# web application at http://3pillars.pythonanywhere.com/
# It works by setting the variable 'application' to a WSGI handler of some
# description.
#
# The below has been auto-generated for your Django project

import os
import sys

# add your project directory to the sys.path
project_home = '/home/3pillars/threepillars'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# set environment variable to tell django where your settings.py is
os.environ['DJANGO_SETTINGS_MODULE'] = 'webcrm.settings'

# serve django via WSGI
try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as e:
    # Log error to a file we can check
    import traceback
    error_file = '/home/3pillars/wsgi_error.log'
    with open(error_file, 'a') as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"WSGI Error: {e}\n")
        f.write(traceback.format_exc())
        f.write(f"{'='*60}\n")
    
    # Re-raise so PythonAnywhere sees it
    raise
