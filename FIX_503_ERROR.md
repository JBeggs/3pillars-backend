# Fix 503 Database Connection Error

## Current Status
- ✅ PostgreSQL service is running
- ✅ Both services in same Railway project
- ❌ App returning 503 "Database connection error"
- ⏳ Code changes not deployed yet

## Steps to Fix

### 1. Push Code Changes
```bash
git push
```
Wait for Railway to deploy (check Railway dashboard → Deployments)

### 2. Check if Migrations Ran
After deployment, check Railway logs:
```bash
railway logs --tail 200 | grep -E "(migrate|migration|release)"
```

Look for:
- `Running release command`
- `Operations to perform:`
- `Applying migrations...`

### 3. If Migrations Didn't Run
Run them manually:
```bash
railway run python manage.py migrate
```

### 4. Check Database Connection
After deployment, check logs for debug output:
```bash
railway logs --tail 100 | grep "DB Config"
```

Should see:
- `[DB Config] Railway container detected (PORT=8080), using internal DATABASE_URL`

### 5. Verify Database URL
In Railway dashboard:
1. Go to Django service → Variables
2. Check `DATABASE_URL` exists
3. Should contain `postgres.railway.internal` (internal connection)

### 6. Test Connection
After deployment, test the login endpoint:
```bash
curl -X POST https://django-crm-production-05d9.up.railway.app/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'
```

Should get:
- `401` (invalid credentials) = ✅ Database connected
- `503` (database error) = ❌ Still failing

## If Still Getting 503 After Deployment

### Check Railway Logs for Errors
```bash
railway logs --tail 500 | grep -E "(ERROR|OperationalError|connection|timeout)"
```

### Possible Issues:
1. **Database paused** - Check PostgreSQL service status
2. **Connection timeout** - Database might be slow to respond
3. **Wrong credentials** - Verify DATABASE_URL is correct
4. **Network issue** - Services might not be properly linked

### Restart Services
1. Restart PostgreSQL service in Railway dashboard
2. Restart Django service (redeploy)
3. Wait 2-3 minutes for both to fully start

### Manual Database Test
Test database connection directly:
```bash
railway connect postgres
```

If this works, the database is accessible. The issue is in Django's connection settings.

## Expected Behavior After Fix

✅ App uses internal `DATABASE_URL` (`postgres.railway.internal`)  
✅ Migrations run successfully  
✅ Login endpoint returns `401` (not `503`)  
✅ Database queries work  

## Debug Output

After deployment, you should see in logs:
```
[DB Config] Railway container detected (PORT=8080), using internal DATABASE_URL
```

If you see this, the code fix is working. If you still get 503, it's a database connectivity issue.

