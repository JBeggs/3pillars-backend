#!/usr/bin/env python
"""
Find the exact error causing the 502.
Run this on PythonAnywhere to see what's actually breaking.
"""
import sys
import os
import traceback

print("=" * 60)
print("DIAGNOSING DJANGO STARTUP ERROR")
print("=" * 60)

# Step 1: Check error log
print("\n1. Checking error log...")
error_log_path = os.path.expanduser('~/logs/error.log')
if os.path.exists(error_log_path):
    print(f"   Reading: {error_log_path}")
    try:
        with open(error_log_path, 'r') as f:
            lines = f.readlines()
            # Show last 50 lines
            print("\n   LAST 50 LINES OF ERROR LOG:")
            print("   " + "-" * 56)
            for line in lines[-50:]:
                print(f"   {line.rstrip()}")
    except Exception as e:
        print(f"   Could not read error log: {e}")
else:
    print(f"   Error log not found at: {error_log_path}")
    print("   Trying alternative locations...")
    alt_paths = [
        '~/logs/user/error.log',
        '~/logs/3pillars/error.log',
        '/var/log/error.log',
    ]
    for path in alt_paths:
        full_path = os.path.expanduser(path)
        if os.path.exists(full_path):
            print(f"   Found: {full_path}")
            with open(full_path, 'r') as f:
                lines = f.readlines()
                for line in lines[-30:]:
                    print(f"   {line.rstrip()}")
            break

# Step 2: Test Django import
print("\n2. Testing Django import...")
try:
    import django
    print("   ✓ Django imported")
except Exception as e:
    print(f"   ✗ Django import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Step 3: Test settings import
print("\n3. Testing settings import...")
try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webcrm.settings')
    django.setup()
    print("   ✓ Django setup successful")
except Exception as e:
    print(f"   ✗ Django setup FAILED: {e}")
    print("\n   FULL TRACEBACK:")
    traceback.print_exc()
    sys.exit(1)

# Step 4: Test database connection
print("\n4. Testing database connection...")
try:
    from django.db import connection
    connection.ensure_connection()
    print("   ✓ Database connection successful")
except Exception as e:
    print(f"   ✗ Database connection FAILED: {e}")
    traceback.print_exc()

# Step 5: Test imports
print("\n5. Testing module imports...")
modules_to_test = [
    'ecommerce.views',
    'ecommerce.models',
    'ecommerce.serializers',
]

for module_name in modules_to_test:
    try:
        __import__(module_name)
        print(f"   ✓ {module_name} imported")
    except Exception as e:
        print(f"   ✗ {module_name} import FAILED: {e}")
        traceback.print_exc()

print("\n" + "=" * 60)
print("DIAGNOSIS COMPLETE")
print("=" * 60)

