#!/usr/bin/env python
"""
Test script to check if Django can import all modules without errors.
Run this on PythonAnywhere to find import errors.
"""
import sys
import os

# Add project directory to path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

print("Testing imports...")

try:
    print("1. Testing Django setup...")
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webcrm.settings')
    django.setup()
    print("   ✓ Django setup OK")
    
    print("2. Testing settings import...")
    from django.conf import settings
    print(f"   ✓ Settings loaded: DEBUG={settings.DEBUG}")
    print(f"   ✓ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"   ✓ MEDIA_ROOT: {settings.MEDIA_ROOT}")
    
    print("3. Testing ecommerce views...")
    from ecommerce import views
    print("   ✓ ecommerce.views imported")
    
    print("4. Testing models...")
    from ecommerce.models import EcommerceProduct, ProductImage
    print("   ✓ Models imported")
    
    print("5. Testing serializers...")
    from ecommerce.serializers import EcommerceProductSerializer
    print("   ✓ Serializers imported")
    
    print("\n✅ All imports successful! Server should start.")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

