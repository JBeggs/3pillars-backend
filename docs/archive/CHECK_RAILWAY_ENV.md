# Check Railway Environment Variables

## Quick Check Commands

### 1. Check if DATABASE_PUBLIC_URL is set:
```bash
railway run env | grep DATABASE_PUBLIC_URL
```

### 2. Check all DATABASE variables:
```bash
railway run env | grep DATABASE
```

### 3. Test database URL selection:
```bash
railway run python -c "
import os
print('DATABASE_PUBLIC_URL:', 'SET' if os.environ.get('DATABASE_PUBLIC_URL') else 'NOT SET')
print('DATABASE_URL:', os.environ.get('DATABASE_URL', 'NOT SET')[:60])
"
```

## If DATABASE_PUBLIC_URL is NOT SET

Railway should automatically set `DATABASE_PUBLIC_URL` when you add a PostgreSQL service, but sometimes it doesn't. 

### Solution 1: Check Railway Dashboard
1. Go to Railway → PostgreSQL Service → Variables
2. Look for `DATABASE_PUBLIC_URL`
3. If missing, Railway might not have set it automatically

### Solution 2: Manually Add DATABASE_PUBLIC_URL
1. Go to Railway → PostgreSQL Service → Variables
2. Copy the `DATABASE_URL` value
3. Replace `postgres.railway.internal` with the public proxy hostname
4. Or get it from Railway → PostgreSQL Service → Connect → Public Proxy

### Solution 3: Use Railway CLI to get it
```bash
railway variables --service <postgres-service-name>
```

## Expected Output

When running `railway run env | grep DATABASE`, you should see:
```
DATABASE_PUBLIC_URL=postgresql://postgres:pass@crossover.proxy.rlwy.net:37952/railway
DATABASE_URL=postgresql://postgres:pass@postgres.railway.internal:5432/railway
```

If `DATABASE_PUBLIC_URL` is missing, that's why `railway run` commands fail!

