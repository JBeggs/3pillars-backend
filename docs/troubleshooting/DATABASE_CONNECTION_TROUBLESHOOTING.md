# Database Connection Error - Troubleshooting Guide

## Before Deleting Database - Try These First

**⚠️ WARNING: Deleting the database will DELETE ALL DATA. Only do this as a last resort.**

---

## Step 1: Check Database Service Status

### In Railway Dashboard:
1. Go to your **PostgreSQL service** (not Django service)
2. Check if it shows:
   - ✅ **"Active"** (green status)
   - ❌ **"Paused"** (if paused, click "Resume")
   - ❌ **"Stopped"** (if stopped, start it)

**If database is paused/stopped:**
- Click "Resume" or "Start"
- Wait 30 seconds for it to wake up
- Try your app again

---

## Step 2: Verify Environment Variables

### Check Django Service Variables:
1. Go to **Django Service** → **Variables** tab
2. Look for these variables:

**Required:**
- `DATABASE_URL` - Should exist and contain `postgres.railway.internal`
- `DATABASE_PUBLIC_URL` - Should exist and contain `crossover.proxy.rlwy.net` or similar
- `PORT` - Should be set (usually `8080`)

**If `DATABASE_URL` is missing:**
- Go to **PostgreSQL Service** → **Variables**
- Copy the `DATABASE_URL` value
- Go to **Django Service** → **Variables** → **"New Variable"**
- Name: `DATABASE_URL`
- Value: Paste the value from PostgreSQL service
- Save

**If `DATABASE_PUBLIC_URL` is missing:**
- Go to **PostgreSQL Service** → **Variables**
- Copy `DATABASE_URL`
- Replace `postgres.railway.internal` with the public proxy hostname
- Or go to **PostgreSQL Service** → **Connect** → **Public Proxy** to get the URL
- Add it as `DATABASE_PUBLIC_URL` in Django Service variables

---

## Step 3: Verify Service Linking

### Check Both Services Are in Same Project:
1. In Railway Dashboard, you should see:
   - Django service
   - PostgreSQL service
   - **Both in the same project** (not separate projects)

**If services are in different projects:**
- They can't communicate via internal network
- You'll need to use `DATABASE_PUBLIC_URL` (public proxy)
- Or move one service to the other's project

---

## Step 4: Check if Migrations Ran

### Check Deployment Logs:
1. Go to **Django Service** → **Deployments** (or check latest deployment)
2. Click **"View Logs"** or **"Logs"**
3. Look for:
   - `=== RELEASE COMMAND STARTING ===`
   - `Operations to perform:`
   - `Applying migrations...`
   - `Running migrations...`

**If you DON'T see migration output:**
- Migrations didn't run
- This is likely why you're getting connection errors
- See "Step 5: Run Migrations Manually"

---

## Step 5: Run Migrations Manually

### Option A: Via Railway Web Shell (if available)
1. Find the shell/console (see `FIND_RAILWAY_SHELL.md`)
2. Run: `python manage.py migrate`
3. Wait for completion

### Option B: Via Railway CLI
```bash
cd /Users/jodybeggs/Documents/new-crm/django-crm
railway run python manage.py migrate
```

**If Railway CLI gives "No such file or directory":**
- Code might not be synced
- Try pushing code first: `git push`
- Then try Railway CLI again

### Option C: Trigger Redeploy
1. Go to **Django Service** → **Settings**
2. Look for **"Redeploy"** or **"Deploy"** button
3. Click it to trigger a new deployment
4. This will run the `release` command (which runs migrations)

---

## Step 6: Test Database Connection

### Test from Railway CLI:
```bash
railway run python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webcrm.settings')
django.setup()
from django.db import connection
try:
    connection.ensure_connection()
    print('✅ Database connection successful!')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"
```

---

## Step 7: Check Database Connection String

### Verify Which URL Is Being Used:
1. Check Railway logs for:
   - `[DB Config] ✅ Using DATABASE_PUBLIC_URL`
   - `[DB Config] ⚠️ Using internal DATABASE_URL`
   - `[DB Config] ❌ No database URL found`

**If you see "No database URL found":**
- Environment variables aren't set
- Go back to Step 2

**If you see connection timeout errors:**
- Database might be sleeping (free tier)
- Wait 30 seconds and try again
- Or upgrade Railway plan

---

## Step 8: Check Database Credentials

### Verify Credentials Are Correct:
1. Go to **PostgreSQL Service** → **Variables**
2. Check `DATABASE_URL` format:
   ```
   postgresql://postgres:PASSWORD@postgres.railway.internal:5432/railway
   ```
3. Make sure password doesn't have special characters that break URL parsing

**If credentials look wrong:**
- Railway might have regenerated them
- Copy fresh `DATABASE_URL` from PostgreSQL service
- Update Django service variables

---

## Step 9: Check for Database Lock/Connection Pool Issues

### Symptoms:
- Connection works sometimes, fails other times
- "too many connections" errors
- "connection pool exhausted" errors

### Fix:
- Check `CONN_MAX_AGE` in `settings.py` (should be 300)
- Reduce Gunicorn workers if using too many connections
- Check PostgreSQL service limits

---

## Step 10: Last Resort - Delete and Recreate Database

**⚠️ THIS WILL DELETE ALL DATA ⚠️**

### Only do this if:
- ✅ All above steps failed
- ✅ You don't have important data in the database
- ✅ You've verified environment variables are correct
- ✅ You've confirmed services are linked

### Steps:
1. **Backup any important data first** (if you have any)
2. Go to **PostgreSQL Service** → **Settings**
3. Scroll to bottom
4. Click **"Delete Service"** or **"Remove"**
5. Confirm deletion
6. Wait for deletion to complete
7. Add new PostgreSQL service:
   - Click **"+ New"** → **"Database"** → **"Add PostgreSQL"**
8. Railway will automatically:
   - Create new database
   - Set `DATABASE_URL` and `DATABASE_PUBLIC_URL`
   - Link it to Django service
9. **Run migrations:**
   - Trigger redeploy, OR
   - Run `railway run python manage.py migrate`

---

## Quick Diagnostic Commands

### Check Environment Variables:
```bash
railway run env | grep DATABASE
```

### Test Database Connection:
```bash
railway run python manage.py dbshell
```

### Check Django Settings:
```bash
railway run python manage.py shell -c "
from django.conf import settings
print('Database:', settings.DATABASES['default']['NAME'])
print('Host:', settings.DATABASES['default'].get('HOST', 'N/A'))
"
```

---

## Common Error Messages and Fixes

### "Database connection error. Please try again later."
- **Cause:** Migrations haven't run OR database is paused
- **Fix:** Run migrations (Step 5) OR resume database (Step 1)

### "could not translate host name 'postgres.railway.internal'"
- **Cause:** Using internal URL from local machine
- **Fix:** Use `DATABASE_PUBLIC_URL` for local `railway run` commands

### "connection timeout expired"
- **Cause:** Database is sleeping (free tier) OR connection pool exhausted
- **Fix:** Wait 30 seconds OR reduce connection pool size

### "relation does not exist"
- **Cause:** Migrations haven't run
- **Fix:** Run migrations (Step 5)

### "503 Service Unavailable"
- **Cause:** Database connection failed OR migrations missing
- **Fix:** Follow Steps 1-5 above

---

## Summary: What to Try First

1. ✅ **Check database service is Active** (Step 1)
2. ✅ **Verify environment variables** (Step 2)
3. ✅ **Check service linking** (Step 3)
4. ✅ **Run migrations manually** (Step 5)
5. ✅ **Test connection** (Step 6)
6. ❌ **Delete database** (Step 10) - Only if all else fails

---

## Still Having Issues?

Before deleting the database, check:
- Railway service status page: https://status.railway.app
- Railway documentation: https://docs.railway.app
- Your Railway project logs for specific error messages

