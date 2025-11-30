# Working with Railway PostgreSQL Database

## ⚠️ Important: Railway PostgreSQL is Managed

Railway's PostgreSQL runs in a managed container. You **cannot** access `/var/lib/postgresql/data` directly because:
- Railway manages the filesystem
- You don't have shell access to the PostgreSQL container
- Files are stored in Railway's infrastructure

## ✅ What You CAN Do Instead

### Option 1: Use Django's Database Shell (Recommended)

Django provides `dbshell` which gives you direct SQL access:

```bash
# Via Railway CLI (if files are synced)
railway run python manage.py dbshell

# This opens a PostgreSQL prompt where you can run SQL:
# railway=# SELECT * FROM information_schema.tables WHERE table_schema = 'public';
# railway=# \dt  (list all tables)
# railway=# \q  (quit)
```

**Note:** Railway CLI might give "No such file or directory" - see Option 2 below.

---

### Option 2: Use Django Shell to Check Database State

Check if tables exist, run queries, inspect database:

```python
# Via Railway CLI
railway run python manage.py shell

# Then in Python shell:
from django.db import connection
cursor = connection.cursor()

# Check if tables exist
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
    ORDER BY table_name;
""")
tables = cursor.fetchall()
print("Tables:", [t[0] for t in tables])

# Check if migrations ran
from django.db.migrations.recorder import MigrationRecorder
migrations = MigrationRecorder.Migration.objects.all()
print("Migrations:", list(migrations.values_list('app', 'name')))

# Check specific table exists
cursor.execute("""
    SELECT 1 FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_name = 'settings_massmailsettings'
""")
exists = cursor.fetchone()
print("massmailsettings table exists:", bool(exists))
```

---

### Option 3: Check Database via Django Management Commands

#### Check Migration Status:
```bash
railway run python manage.py showmigrations
```

This shows which migrations have been applied (marked with `[X]`).

#### Check Specific App Migrations:
```bash
railway run python manage.py showmigrations settings
railway run python manage.py showmigrations common
```

#### List All Tables (via Django):
```bash
railway run python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
cursor.execute(\"\"\"
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
    ORDER BY table_name
\"\"\")
for row in cursor.fetchall():
    print(row[0])
"
```

---

### Option 4: Connect via External Tool (pgAdmin, DBeaver, etc.)

1. **Get Connection Details:**
   ```bash
   railway run env | grep DATABASE_PUBLIC_URL
   ```

2. **Parse the URL:**
   ```
   postgresql://postgres:PASSWORD@crossover.proxy.rlwy.net:37952/railway
   ```
   - Host: `crossover.proxy.rlwy.net`
   - Port: `37952`
   - Database: `railway`
   - User: `postgres`
   - Password: (from URL)

3. **Connect with pgAdmin/DBeaver:**
   - Use the public proxy URL (from `DATABASE_PUBLIC_URL`)
   - This allows external connections

---

### Option 5: Use Railway CLI Database Connection

```bash
# Connect directly to PostgreSQL
railway connect postgres

# This opens a psql prompt where you can run SQL
```

**Note:** This might not work if Railway CLI can't find the service.

---

## 🔍 Quick Diagnostic: Check if Migrations Ran

### Check if Tables Exist:

```bash
railway run python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()

# Check for critical tables
tables_to_check = [
    'settings_massmailsettings',
    'settings_reminders',
    'django_migrations',
    'auth_user',
]

for table in tables_to_check:
    cursor.execute(f\"\"\"
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = '{table}'
    \"\"\")
    exists = cursor.fetchone()
    print(f'{table}: {\"✅ EXISTS\" if exists else \"❌ MISSING\"}')
"
```

### Check Migration Status:

```bash
railway run python manage.py showmigrations --list | head -20
```

---

## 🛠️ Common Tasks

### 1. Check Database Connection Works:

```bash
railway run python manage.py shell -c "
from django.db import connection
try:
    connection.ensure_connection()
    print('✅ Database connection successful!')
    with connection.cursor() as cursor:
        cursor.execute('SELECT version();')
        print('PostgreSQL:', cursor.fetchone()[0][:50])
except Exception as e:
    print(f'❌ Connection failed: {e}')
"
```

### 2. List All Tables:

```bash
railway run python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
cursor.execute(\"\"\"
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
    ORDER BY table_name
\"\"\")
print('Tables in database:')
for row in cursor.fetchall():
    print('  -', row[0])
"
```

### 3. Check if Specific Table Exists:

```bash
railway run python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
cursor.execute(\"\"\"
    SELECT 1 FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_name = 'settings_massmailsettings'
\"\"\")
result = cursor.fetchone()
print('massmailsettings table exists:', bool(result))
"
```

### 4. Count Rows in Table:

```bash
railway run python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT COUNT(*) FROM django_migrations')
count = cursor.fetchone()[0]
print(f'Total migrations applied: {count}')
"
```

### 5. Run Raw SQL Query:

```bash
railway run python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT table_name FROM information_schema.tables WHERE table_schema = \\'public\\' LIMIT 10')
for row in cursor.fetchall():
    print(row[0])
"
```

---

## 🚨 If Railway CLI Doesn't Work

If `railway run` gives "No such file or directory", you need to:

1. **Push code to Railway:**
   ```bash
   git add .
   git commit -m "Check database state"
   git push
   ```

2. **Wait for deployment to complete**

3. **Then try Railway CLI again**

OR

4. **Use Railway Web Shell** (if you can find it - see `FIND_RAILWAY_SHELL.md`)

---

## 📊 Alternative: Check via API/Django Admin

If the app is running, you can check database state via:

1. **Django Admin:** `https://your-app.railway.app/<admin-prefix>/`
2. **API Endpoints:** Check if endpoints return data (indicates tables exist)

---

## Summary

**You CANNOT:**
- ❌ Access `/var/lib/postgresql/data` directly
- ❌ SSH into PostgreSQL container
- ❌ Access PostgreSQL filesystem

**You CAN:**
- ✅ Use `python manage.py dbshell` for SQL access
- ✅ Use `python manage.py shell` for Python/Django access
- ✅ Use `python manage.py showmigrations` to check migration status
- ✅ Connect via external tools (pgAdmin, DBeaver) using `DATABASE_PUBLIC_URL`
- ✅ Use Railway CLI: `railway connect postgres`

**For your current issue (database connection error):**
1. First check if migrations ran: `railway run python manage.py showmigrations`
2. Check if tables exist: Use Option 2 or 3 above
3. If tables don't exist, run migrations: `railway run python manage.py migrate`

