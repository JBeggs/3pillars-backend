#!/usr/bin/env python
"""
Quick script to check and fix admin access for your user.
Run: python check_admin_access.py
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webcrm.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Get your username from command line or use default
username = sys.argv[1] if len(sys.argv) > 1 else input("Enter your username: ").strip()

try:
    user = User.objects.get(username=username)
    
    print(f"\n📋 User: {user.username} ({user.email})")
    print(f"   is_staff: {user.is_staff}")
    print(f"   is_superuser: {user.is_superuser}")
    print(f"   is_active: {user.is_active}")
    
    if not user.is_staff or not user.is_superuser:
        print("\n⚠️  User doesn't have admin access!")
        fix = input("Fix it? (y/n): ").strip().lower()
        if fix == 'y':
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.save()
            print("✅ Fixed! User now has admin access.")
            print(f"   is_staff: {user.is_staff}")
            print(f"   is_superuser: {user.is_superuser}")
        else:
            print("❌ Not fixed. User still can't access admin.")
    else:
        print("\n✅ User has admin access!")
        
    # Check if news models are registered
    from django.contrib import admin
    from news.models import Article, Profile, Category
    
    print("\n📰 Checking News models in admin:")
    print(f"   Article registered: {admin.site.is_registered(Article)}")
    print(f"   Profile registered: {admin.site.is_registered(Profile)}")
    print(f"   Category registered: {admin.site.is_registered(Category)}")
    
    if not admin.site.is_registered(Article):
        print("⚠️  News models not registered! Try restarting Django server.")
    else:
        print("✅ News models are registered!")
        
except User.DoesNotExist:
    print(f"❌ User '{username}' not found!")
    print("\nAvailable users:")
    for u in User.objects.all()[:10]:
        print(f"   - {u.username} ({u.email})")

