#!/usr/bin/env python
"""
Quick email test script.
Usage: python test_email.py your-email@example.com
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webcrm.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_email(recipient_email):
    """Send a test email."""
    print(f"Testing email configuration...")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print(f"\nSending test email to: {recipient_email}")
    
    try:
        send_mail(
            subject='Django CRM Test Email',
            message='This is a test email from Django CRM. If you receive this, email configuration is working correctly!',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        print("✅ Email sent successfully!")
        print(f"Check your inbox at {recipient_email}")
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        print("\nTroubleshooting:")
        print("1. Check EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD in .env")
        print("2. For Gmail, use App Password (not regular password)")
        print("3. Check firewall/network settings")
        print("4. Verify SMTP credentials are correct")
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python test_email.py your-email@example.com")
        sys.exit(1)
    
    recipient = sys.argv[1]
    test_email(recipient)

