#!/usr/bin/env python
"""
Quick check script to verify Django can start without errors.
Run this on PythonAnywhere to check for import/syntax errors.
"""
import os
import sys
import django

# Add project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webcrm.settings')

try:
    django.setup()
    print("✓ Django setup successful")
    
    # Try importing views
    from ecommerce import views
    print("✓ ecommerce.views imported successfully")
    
    # Try importing models
    from ecommerce.models import ProductImage
    print("✓ ecommerce.models imported successfully")
    
    # Check MEDIA_ROOT
    from django.conf import settings
    print(f"✓ MEDIA_ROOT: {settings.MEDIA_ROOT}")
    print(f"✓ MEDIA_URL: {settings.MEDIA_URL}")
    
    print("\n✓ All checks passed! Server should start correctly.")
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

