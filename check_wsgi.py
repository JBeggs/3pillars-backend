#!/usr/bin/env python
"""
Test WSGI application directly to see if it works.
"""
import os
import sys

# Add project directory
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webcrm.settings')

print("Testing WSGI application...")

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    print("✓ WSGI application created successfully!")
    print(f"✓ Application type: {type(application)}")
except Exception as e:
    print(f"✗ WSGI application creation FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

