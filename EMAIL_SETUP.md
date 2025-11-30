# Email Configuration Guide

Setting up email in Django is straightforward. This guide covers configuration for various email providers.

## Quick Setup

### 1. Add to `.env` File

Add these variables to your `django-crm/.env` file:

```env
# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
DEFAULT_FROM_EMAIL=your-email@gmail.com
SERVER_EMAIL=your-email@gmail.com
CRM_REPLY_TO=your-email@gmail.com

# Admin emails (for error reports)
# Format: "Name1:email1@example.com,Name2:email2@example.com"
ADMINS=Admin:admin@yourdomain.com
```

### 2. Restart Django Server

After updating `.env`, restart your Django server for changes to take effect.

## Email Provider Configurations

### Gmail

**Settings:**
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password  # NOT your regular password!
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

**Important:** You need to use an **App Password**, not your regular Gmail password.

**How to get Gmail App Password:**
1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Security → 2-Step Verification (must be enabled)
3. App passwords → Generate new app password
4. Use the generated 16-character password

### Custom Domain (cPanel, Hosting Provider)

**Settings:**
```env
EMAIL_HOST=mail.yourdomain.com  # or smtp.yourdomain.com
EMAIL_HOST_USER=your-email@yourdomain.com
EMAIL_HOST_PASSWORD=your-email-password
EMAIL_PORT=587  # or 465 for SSL
EMAIL_USE_TLS=True  # True for port 587
EMAIL_USE_SSL=False  # True for port 465
DEFAULT_FROM_EMAIL=your-email@yourdomain.com
```

**Common SMTP Settings:**
- **Port 587 (TLS)**: `EMAIL_USE_TLS=True`, `EMAIL_USE_SSL=False`
- **Port 465 (SSL)**: `EMAIL_USE_TLS=False`, `EMAIL_USE_SSL=True`
- **Port 25**: Usually blocked by ISPs, not recommended

### Outlook/Office 365

**Settings:**
```env
EMAIL_HOST=smtp.office365.com
EMAIL_HOST_USER=your-email@outlook.com
EMAIL_HOST_PASSWORD=your-password
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
DEFAULT_FROM_EMAIL=your-email@outlook.com
```

### SendGrid

**Settings:**
```env
EMAIL_HOST=smtp.sendgrid.net
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

### Mailgun

**Settings:**
```env
EMAIL_HOST=smtp.mailgun.org
EMAIL_HOST_USER=your-mailgun-smtp-username
EMAIL_HOST_PASSWORD=your-mailgun-smtp-password
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

### Amazon SES

**Settings:**
```env
EMAIL_HOST=email-smtp.us-east-1.amazonaws.com  # Use your region
EMAIL_HOST_USER=your-ses-smtp-username
EMAIL_HOST_PASSWORD=your-ses-smtp-password
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

## Testing Email Configuration

### Method 1: Django Shell

```bash
cd django-crm
source venv/bin/activate
python manage.py shell
```

Then run:
```python
from django.core.mail import send_mail

send_mail(
    subject='Test Email',
    message='This is a test email from Django CRM.',
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=['your-email@example.com'],
    fail_silently=False,
)
```

### Method 2: Management Command

Create a test command:
```bash
python manage.py sendtestemail your-email@example.com
```

### Method 3: Check Settings

```python
python manage.py shell
from django.conf import settings

print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
```

## Common Issues

### "Authentication failed"

**Solutions:**
1. **Gmail**: Use App Password, not regular password
2. **2FA Required**: Enable 2-factor authentication and use app password
3. **Wrong Credentials**: Double-check username and password
4. **Less Secure Apps**: Some providers require enabling "less secure apps" (not recommended)

### "Connection timeout"

**Solutions:**
1. Check firewall settings
2. Verify SMTP host and port are correct
3. Try different port (587 vs 465)
4. Check if your hosting provider blocks SMTP ports

### "SSL/TLS errors"

**Solutions:**
1. Ensure `EMAIL_USE_TLS` and `EMAIL_USE_SSL` are set correctly:
   - Port 587: `EMAIL_USE_TLS=True`, `EMAIL_USE_SSL=False`
   - Port 465: `EMAIL_USE_TLS=False`, `EMAIL_USE_SSL=True`
2. Check if your Python has SSL support

### Emails going to spam

**Solutions:**
1. Set up SPF record in DNS
2. Set up DKIM record in DNS
3. Set up DMARC record in DNS
4. Use a proper "From" address matching your domain
5. Avoid spam trigger words in subject/body

## DNS Records for Email

For custom domain emails, set up these DNS records:

### SPF Record
```
Type: TXT
Name: @ (or yourdomain.com)
Value: v=spf1 include:_spf.google.com ~all
```

### DKIM Record
Get from your email provider (varies by provider)

### DMARC Record
```
Type: TXT
Name: _dmarc
Value: v=DMARC1; p=none; rua=mailto:admin@yourdomain.com
```

## Security Best Practices

1. **Never commit `.env` file** - Already in `.gitignore` ✅
2. **Use App Passwords** - Don't use main account passwords
3. **Use Environment Variables** - Don't hardcode credentials
4. **Enable 2FA** - On your email account
5. **Use TLS/SSL** - Always encrypt email connections
6. **Limit Admin Emails** - Only add trusted email addresses

## Production Checklist

- [ ] Email settings configured in `.env`
- [ ] Test email sent successfully
- [ ] SPF record configured
- [ ] DKIM record configured (if available)
- [ ] DMARC record configured
- [ ] `DEFAULT_FROM_EMAIL` matches your domain
- [ ] Admin emails configured for error reports
- [ ] Email timeout set appropriately
- [ ] TLS/SSL enabled

## Usage in Code

### Send Simple Email

```python
from django.core.mail import send_mail

send_mail(
    subject='Welcome!',
    message='Thank you for joining.',
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=['user@example.com'],
)
```

### Send HTML Email

```python
from django.core.mail import EmailMessage

email = EmailMessage(
    subject='Order Confirmation',
    body='<h1>Your order has been confirmed!</h1>',
    from_email=settings.DEFAULT_FROM_EMAIL,
    to=['customer@example.com'],
)
email.content_subtype = 'html'
email.send()
```

### Send Email with Attachments

```python
from django.core.mail import EmailMessage

email = EmailMessage(
    subject='Invoice',
    body='Please find attached invoice.',
    from_email=settings.DEFAULT_FROM_EMAIL,
    to=['customer@example.com'],
)
email.attach_file('/path/to/invoice.pdf')
email.send()
```

## PythonAnywhere Specific

PythonAnywhere may have restrictions on SMTP. Check their documentation or use:
- SendGrid
- Mailgun
- Amazon SES
- Or configure through their email settings

## Next Steps

1. ✅ Add email settings to `.env`
2. ✅ Test email sending
3. ✅ Configure DNS records (for custom domain)
4. ✅ Set up admin emails for error reports
5. ✅ Test password reset emails
6. ✅ Test order confirmation emails (for e-commerce)

Email setup is complete once you can send a test email successfully!

