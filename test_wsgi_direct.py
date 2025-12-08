#!/usr/bin/env python
"""
Test the WSGI file directly to see if it works.
Run this on PythonAnywhere.
"""
import os
import sys

# Simulate what PythonAnywhere does
project_home = '/home/3pillars/threepillars'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['DJANGO_SETTINGS_MODULE'] = 'webcrm.settings'

print("Testing WSGI application creation...")
print(f"Python path: {sys.path[:3]}")
print(f"Settings module: {os.environ['DJANGO_SETTINGS_MODULE']}")

try:
    from django.core.wsgi import get_wsgi_application
    print("✓ get_wsgi_application imported")
    
    print("Creating WSGI application...")
    application = get_wsgi_application()
    print(f"✓ WSGI application created: {type(application)}")
    
    # Test a simple request simulation
    print("\nTesting application call...")
    def start_response(status, headers):
        print(f"  Status: {status}")
        return None
    
    environ = {
        'REQUEST_METHOD': 'GET',
        'PATH_INFO': '/',
        'SERVER_NAME': 'test',
        'SERVER_PORT': '80',
    }
    
    result = application(environ, start_response)
    print("✓ Application call successful!")
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✓ All tests passed! WSGI should work.")

