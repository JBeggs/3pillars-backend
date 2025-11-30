# PythonAnywhere Deployment Checklist

Use this checklist to ensure a smooth deployment.

## Pre-Deployment

### Code Preparation
- [ ] All code committed to git
- [ ] All migrations created: `python manage.py makemigrations`
- [ ] Test migrations locally: `python manage.py migrate`
- [ ] Test application locally
- [ ] Update `runtime.txt` if needed (Python 3.11)

### Environment Variables
- [ ] Generate new `SECRET_KEY`
- [ ] Prepare `.env` file with all required variables
- [ ] Verify `DEBUG=False` for production
- [ ] Set `ALLOWED_HOSTS` correctly

### Database
- [ ] Create MySQL database on PythonAnywhere
- [ ] Note database credentials
- [ ] Test database connection locally (if possible)

### Files to Upload
- [ ] `firebase-service-account.json` (if using FCM)
- [ ] Any other required files

## Deployment Steps

### 1. Initial Setup
- [ ] Clone repository on PythonAnywhere
- [ ] Create virtual environment (Python 3.11)
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Create `.env` file with production values
- [ ] Upload `firebase-service-account.json` (if needed)

### 2. Database Setup
- [ ] Run migrations: `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Create default products: `python manage.py create_default_products`
- [ ] Verify database connection works

### 3. Static Files
- [ ] Collect static files: `python manage.py collectstatic --noinput`
- [ ] Verify files in `~/static/static/`
- [ ] Configure static files mapping in Web tab

### 4. Media Files
- [ ] Create media directory: `mkdir -p ~/media`
- [ ] Set permissions: `chmod 755 ~/media`
- [ ] Configure media files mapping in Web tab

### 5. WSGI Configuration
- [ ] Update WSGI file with correct paths
- [ ] Replace `yourusername` with actual username
- [ ] Verify virtual environment path
- [ ] Test WSGI file syntax

### 6. Web App Configuration
- [ ] Set Python version (3.11)
- [ ] Configure source code directory
- [ ] Set working directory
- [ ] Map static files URLs
- [ ] Map media files URLs

### 7. Final Steps
- [ ] Reload web app
- [ ] Check error log for issues
- [ ] Test admin panel login
- [ ] Test API endpoints
- [ ] Verify static files load
- [ ] Test file uploads (media)

## Post-Deployment Verification

### Functionality Tests
- [ ] Admin panel accessible and functional
- [ ] Can log in as superuser
- [ ] Can create/edit records
- [ ] API endpoints respond correctly
- [ ] Static files (CSS/JS) load
- [ ] Images display correctly
- [ ] File uploads work
- [ ] Database queries work

### Security Checks
- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` (not default)
- [ ] `.env` file has correct permissions (`chmod 600`)
- [ ] `firebase-service-account.json` not publicly accessible
- [ ] HTTPS enabled (automatic on PythonAnywhere)

### Performance Checks
- [ ] Page load times acceptable
- [ ] Static files served efficiently
- [ ] Database queries optimized
- [ ] No memory leaks

## Troubleshooting

If something doesn't work:

1. **Check Error Logs:**
   - Web tab → Error log
   - Web tab → Server log

2. **Common Issues:**
   - Database connection: Check credentials in `.env`
   - Static files: Verify mapping and `collectstatic` ran
   - Import errors: Check virtual environment path in WSGI
   - 500 errors: Enable `DEBUG=True` temporarily to see details

3. **Get Help:**
   - PythonAnywhere help: https://help.pythonanywhere.com/
   - Check application logs: `tail -f ~/logs/yourusername.pythonanywhere.com.error.log`

## Update Procedure

When updating the application:

- [ ] Pull latest code: `git pull`
- [ ] Activate virtual environment: `source venv/bin/activate`
- [ ] Update dependencies: `pip install -r requirements.txt`
- [ ] Run migrations: `python manage.py migrate`
- [ ] Collect static files: `python manage.py collectstatic --noinput`
- [ ] Reload web app
- [ ] Test functionality
- [ ] Check error logs

---

**Save this checklist and check off items as you complete them!**

