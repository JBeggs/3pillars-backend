# Railway Build Error Fix

## Problem
Railway is trying to run `python manage.py setupdata` during the **build phase**, but the database isn't available then. This causes:
```
✗ Migration error: could not translate host name "postgres.railway.internal" to address: Name or service not known
```

## Solution
The `setupdata` command now detects if it's being run during build phase and exits gracefully without failing the build.

## What Changed
- `setupdata` checks if database is available
- If database isn't available (build phase), it skips and shows a warning
- Migrations will still run during **release phase** (via Procfile)

## Railway Build Process

1. **Build Phase** (no database):
   - Installs dependencies
   - Builds Docker image
   - `setupdata` detects no database → skips gracefully ✅

2. **Release Phase** (database available):
   - Runs `Procfile` release command
   - Executes `run_migrations.py` → runs migrations ✅
   - Collects static files ✅

3. **Runtime** (database available):
   - App runs with Gunicorn
   - Database fully accessible ✅

## Manual Setup (If Needed)

If you need to run `setupdata` manually (e.g., to load fixtures or create superuser):

```bash
railway run python manage.py setupdata
```

Or skip fixtures if they hang:
```bash
railway run python manage.py setupdata --skip-fixtures
```

## Verify It Works

After deployment:
1. Check Railway logs - should see migrations running in release phase
2. Check app is running - should connect to database
3. If needed, run setupdata manually for fixtures/superuser

## Summary

✅ **Build phase**: setupdata skips gracefully (no database)
✅ **Release phase**: Migrations run automatically (via Procfile)
✅ **Runtime**: App connects to database successfully

The build should now complete successfully!

