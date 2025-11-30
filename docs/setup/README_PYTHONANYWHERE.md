# Django CRM - PythonAnywhere Ready

This Django CRM application has been configured for deployment on PythonAnywhere.

## What Changed

### Removed Railway-Specific Files
- ✅ Removed `Procfile` (not needed for PythonAnywhere)
- ✅ Removed `.railwayignore`
- ✅ Removed `railway_setup.sh`
- ✅ Removed `railway-postdeploy.sh`
- ✅ Removed `run_migrations.py`
- ✅ Moved Railway documentation to `docs/archive/`

### Updated Configuration
- ✅ **Settings** (`webcrm/settings.py`):
  - Removed Railway-specific database configuration
  - Added PythonAnywhere detection
  - Configured MySQL database support
  - Updated static/media file paths for PythonAnywhere
  - Removed WhiteNoise middleware (PythonAnywhere serves static files)

- ✅ **Setup Command** (`common/management/commands/setupdata.py`):
  - Removed Railway-specific build phase detection
  - Simplified database availability check

### Added PythonAnywhere Support
- ✅ Automatic detection of PythonAnywhere environment
- ✅ MySQL database configuration
- ✅ Static files configuration
- ✅ Media files configuration
- ✅ WSGI file ready for PythonAnywhere

## Quick Start

1. **Follow the deployment guide**: See `PYTHONANYWHERE_DEPLOYMENT.md`

2. **Key configuration**:
   - Set environment variables in `.env` file
   - Configure WSGI file in PythonAnywhere dashboard
   - Map static and media files

3. **Database**: Use PythonAnywhere's MySQL database

## Environment Variables

Create a `.env` file with:

```env
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourusername.pythonanywhere.com
DB_NAME=yourusername$crm_db
DB_USER=yourusername
DB_PASSWORD=your-password
DB_HOST=yourusername.mysql.pythonanywhere-services.com
PYTHONANYWHERE_USERNAME=yourusername
```

## Next Steps

1. Read `PYTHONANYWHERE_DEPLOYMENT.md` for detailed setup instructions
2. Deploy to PythonAnywhere following the guide
3. Test your application

## Notes

- The application automatically detects PythonAnywhere environment
- Static files are served by PythonAnywhere (no WhiteNoise needed)
- Media files are stored in `~/media/`
- Database uses MySQL (PythonAnywhere default)

