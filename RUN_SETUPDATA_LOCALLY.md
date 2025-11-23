# How to Run setupdata Locally

## Using Railway CLI (Recommended)

This runs the command in Railway's environment with access to the Railway database:

```bash
cd django-crm
railway run python manage.py setupdata
```

**Options:**
- Skip fixtures if they hang: `railway run python manage.py setupdata --skip-fixtures`
- Verbose output: `railway run python manage.py setupdata --verbosity 2`

## What setupdata Does

1. **Runs migrations** - Creates/updates database tables
2. **Loads fixtures** - Populates initial data (countries, currencies, etc.)
3. **Creates superuser** - Creates admin user with credentials:
   - Username: `IamSUPER`
   - Password: Randomly generated (shown in output)
   - Email: `super@example.com`

## Troubleshooting

### If setupdata hangs:
- Use `--skip-fixtures` to skip fixture loading
- Check Railway database is running and accessible
- Try running migrations separately: `railway run python manage.py migrate`

### If you get connection errors:
- Make sure Railway database service is running
- Check `DATABASE_PUBLIC_URL` is set (for local railway run commands)
- Wait a few seconds and retry (database might be waking up)

### To run migrations only:
```bash
railway run python manage.py migrate
```

### To load fixtures manually:
```bash
railway run python manage.py loaddata country.json currency.json groups.json
```

## Notes

- `railway run` uses Railway's environment variables (DATABASE_PUBLIC_URL)
- The command runs locally but connects to Railway's database
- Superuser password is randomly generated each time
- If superuser already exists, it will skip creation (won't error)

