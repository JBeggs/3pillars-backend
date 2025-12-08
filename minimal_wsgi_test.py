#!/usr/bin/env python
"""
Minimal WSGI test - test each step to find where it hangs.
"""
import os
import sys
import time

project_home = '/home/3pillars/threepillars'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

print("Step 1: Testing basic imports...")
try:
    import django
    print("  ✓ Django imported")
except Exception as e:
    print(f"  ✗ Django import failed: {e}")
    sys.exit(1)

print("\nStep 2: Setting environment...")
os.environ['DJANGO_SETTINGS_MODULE'] = 'webcrm.settings'
print("  ✓ Environment set")

print("\nStep 3: Testing settings import (this might hang)...")
start_time = time.time()
try:
    from django.conf import settings
    elapsed = time.time() - start_time
    print(f"  ✓ Settings imported in {elapsed:.2f}s")
    print(f"    DEBUG: {settings.DEBUG}")
    print(f"    DATABASE: {settings.DATABASES['default']['ENGINE']}")
except Exception as e:
    elapsed = time.time() - start_time
    print(f"  ✗ Settings import failed after {elapsed:.2f}s: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nStep 4: Testing Django setup (this might hang)...")
start_time = time.time()
try:
    django.setup()
    elapsed = time.time() - start_time
    print(f"  ✓ Django setup completed in {elapsed:.2f}s")
except Exception as e:
    elapsed = time.time() - start_time
    print(f"  ✗ Django setup failed after {elapsed:.2f}s: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nStep 5: Testing database connection (this might hang)...")
start_time = time.time()
try:
    from django.db import connection
    connection.ensure_connection()
    elapsed = time.time() - start_time
    print(f"  ✓ Database connection in {elapsed:.2f}s")
except Exception as e:
    elapsed = time.time() - start_time
    print(f"  ✗ Database connection failed after {elapsed:.2f}s: {e}")
    import traceback
    traceback.print_exc()

print("\nStep 6: Testing WSGI application creation...")
start_time = time.time()
try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    elapsed = time.time() - start_time
    print(f"  ✓ WSGI application created in {elapsed:.2f}s")
except Exception as e:
    elapsed = time.time() - start_time
    print(f"  ✗ WSGI application creation failed after {elapsed:.2f}s: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("ALL STEPS PASSED - WSGI SHOULD WORK")
print("="*60)
print("\nIf web app still 502s, check:")
print("1. Virtualenv path in web app config")
print("2. Web app error log (scroll down in Web tab)")
print("3. Make sure you clicked 'Reload' after changes")

