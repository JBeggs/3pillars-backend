# Run Migrations Now - Quick Guide

## Current Situation
- ✅ Code is deployed and using correct database URL
- ✅ App is running (workers starting)
- ❌ Workers timing out because **migrations haven't run**
- ❌ Database tables don't exist yet

## Solution: Run Migrations Manually

### Option 1: Railway Web Shell (Easiest)
1. Go to Railway Dashboard → Django Service
2. Click **"Deployments"** → Latest deployment
3. Click **"Shell"** tab (or "View Logs" → "Shell")
4. Run:
   ```bash
   python manage.py migrate
   ```
5. Wait for it to complete
6. Check output - should see "Operations to perform:" and "Applying migrations..."

### Option 2: Railway CLI (If web shell doesn't work)
```bash
cd django-crm
railway run python manage.py migrate
```

**Note:** This might timeout if database is slow. If it does, try Option 1 (web shell).

### Option 3: Check Release Command Logs
1. Go to Railway Dashboard → Django Service → Deployments
2. Click on latest deployment
3. Look for logs that show:
   - `=== RELEASE COMMAND STARTING ===`
   - `=== RUNNING MIGRATIONS ===`
   - Migration output

If you don't see these, the release command didn't run.

## After Migrations Run

Once migrations complete successfully:
1. ✅ Database tables will exist
2. ✅ Workers should stop timing out
3. ✅ API endpoints should work
4. ✅ Login should return 401 (not 503)

## Verify Migrations Ran

Check migration status:
```bash
railway run python manage.py showmigrations
```

All migrations should show `[X]` (applied), not `[ ]` (pending).

## If Migrations Still Fail

If migrations timeout or fail:
1. **Check PostgreSQL service** - Is it running? (Railway Dashboard)
2. **Restart PostgreSQL** - Might be in a bad state
3. **Wait 2-3 minutes** after restart before retrying
4. **Check Railway status** - https://status.railway.app

## Next Steps After Migrations

1. **Load initial data** (optional):
   ```bash
   railway run python manage.py setupdata --skip-fixtures
   ```

2. **Create superuser** (if needed):
   ```bash
   railway run python manage.py createsuperuser
   ```

3. **Test the API**:
   ```bash
   curl https://django-crm-production-05d9.up.railway.app/api/docs/
   ```

The code is fixed - you just need to run migrations!

