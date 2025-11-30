# Railway Settings Checklist

## Critical Settings to Verify

### 1. Service Linking (CRITICAL)
**Location:** Railway Dashboard → Your Project

**Check:**
- ✅ Django service and PostgreSQL service are in the **same Railway project**
- ✅ Both services show as "Active" (green status)
- ✅ PostgreSQL service is not paused

**If services are in different projects:**
- They can't communicate via internal network
- `DATABASE_URL` won't be auto-set
- You'll need to manually set `DATABASE_URL` with public URL

---

### 2. Environment Variables (CRITICAL)
**Location:** Railway Dashboard → Django Service → Variables Tab

**Required Variables:**
- ✅ `DATABASE_URL` - Should be auto-set by Railway (contains `postgres.railway.internal`)
- ✅ `DATABASE_PUBLIC_URL` - Should be auto-set (contains `crossover.proxy.rlwy.net`)
- ✅ `PORT` - Auto-set by Railway (should be `8080` or similar)
- ✅ `RAILWAY_ENVIRONMENT` - Auto-set (should be `production`)

**Optional but Recommended:**
- `SECRET_KEY` - Django secret key
- `DEBUG` - Set to `False` for production
- `ALLOWED_HOSTS` - Your Railway domain

**To Check:**
1. Go to Django Service → Variables
2. Look for `DATABASE_URL`
3. Click on it to see the value
4. Should contain: `postgres.railway.internal:5432`

---

### 3. Release Command Execution
**Location:** Railway Dashboard → Django Service → Settings → Deploy

**Check:**
- ✅ "Run Release Command" is **enabled**
- ✅ Procfile has `release:` command defined

**If release command isn't running:**
- Migrations won't run automatically
- You'll need to run them manually: `railway run python manage.py migrate`

**To Verify Release Command Ran:**
1. Go to Django Service → Deployments
2. Click on latest deployment
3. Check logs for: `=== RELEASE COMMAND STARTING ===`
4. Or look for migration output

---

### 4. PostgreSQL Service Status
**Location:** Railway Dashboard → PostgreSQL Service

**Check:**
- ✅ Service status is "Active" (green)
- ✅ Service is not paused
- ✅ No error messages in logs

**If paused:**
- Click "Start" or "Resume"
- Wait 2-3 minutes for full startup
- Database connections will fail until it's running

---

### 5. Network/Connectivity Settings
**Location:** Railway Dashboard → Both Services → Settings

**Check:**
- ✅ Both services are in same project (for internal networking)
- ✅ No firewall rules blocking connections
- ✅ Services can communicate internally

**Internal Network:**
- Services in same project can use `postgres.railway.internal`
- This is faster and more reliable than public proxy

---

### 6. Build Settings
**Location:** Railway Dashboard → Django Service → Settings → Build

**Check:**
- ✅ Build command is correct (or auto-detected)
- ✅ Root directory is correct (should be `django-crm` if repo root)
- ✅ Python version matches `runtime.txt` (3.11)

**If build fails:**
- Check build logs for errors
- Verify `requirements.txt` exists
- Check Python version compatibility

---

### 7. Deploy Settings
**Location:** Railway Dashboard → Django Service → Settings → Deploy

**Check:**
- ✅ Start command uses `$PORT` variable
- ✅ Health check is configured (if enabled)
- ✅ Auto-deploy is enabled (if using Git)

---

## Quick Diagnostic Commands

### Check if DATABASE_URL is set:
```bash
railway run env | grep DATABASE_URL
```

### Test database connection:
```bash
railway run python manage.py dbshell
```

### Check migration status:
```bash
railway run python manage.py showmigrations
```

### Run migrations manually:
```bash
railway run python manage.py migrate
```

---

## Common Issues and Fixes

### Issue: Release command not running
**Fix:**
1. Check Railway Settings → Deploy → "Run Release Command" is enabled
2. Verify Procfile has `release:` command
3. Manually run migrations: `railway run python manage.py migrate`

### Issue: DATABASE_URL missing
**Fix:**
1. Ensure PostgreSQL service is in same project
2. Railway auto-sets this when services are linked
3. If missing, manually add it from PostgreSQL service → Variables

### Issue: Database connection timeout
**Fix:**
1. Check PostgreSQL service is running (not paused)
2. Restart PostgreSQL service
3. Verify services are in same project (for internal connection)
4. Check Railway status page for outages

### Issue: Services can't communicate
**Fix:**
1. Ensure both services in same Railway project
2. Check service status (both should be Active)
3. Restart both services if needed

---

## Step-by-Step Verification

1. **Open Railway Dashboard**
   - Go to https://railway.app
   - Log in

2. **Check Project Structure**
   - Click on your project
   - Verify you see both:
     - Django Service (your app)
     - PostgreSQL Service (database)

3. **Check Django Service Variables**
   - Click Django Service → Variables tab
   - Look for `DATABASE_URL`
   - Should contain `postgres.railway.internal`

4. **Check PostgreSQL Service Status**
   - Click PostgreSQL Service
   - Status should be "Active" (green)
   - If paused, click "Start"

5. **Check Latest Deployment**
   - Click Django Service → Deployments
   - Click latest deployment
   - Check logs for release command output
   - Look for migration messages

6. **If Release Command Didn't Run**
   - Go to Settings → Deploy
   - Ensure "Run Release Command" is enabled
   - Or run migrations manually

---

## Still Having Issues?

If after checking all these settings you still have problems:

1. **Check Railway Status:** https://status.railway.app
2. **Restart Services:** Restart both Django and PostgreSQL
3. **Check Logs:** Look for specific error messages
4. **Run Migrations Manually:** `railway run python manage.py migrate`
5. **Test Connection:** `railway run python manage.py dbshell`

