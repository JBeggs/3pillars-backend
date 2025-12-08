"""
Management command to reset the database.
Drops all tables, runs migrations, and optionally repopulates with initial data.
WARNING: This will delete all data!
"""
import os
import sys
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from django.db import connection


class Command(BaseCommand):
    help = "Reset database - drop all tables, run migrations, and optionally repopulate"

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-input',
            action='store_true',
            help='Skip confirmation prompt (use with caution!)',
        )
        parser.add_argument(
            '--repopulate',
            action='store_true',
            help='Repopulate database after reset (runs setupdata)',
        )
        parser.add_argument(
            '--skip-migrations',
            action='store_true',
            help='Skip running migrations after reset',
        )
        parser.add_argument(
            '--flush-only',
            action='store_true',
            help='Use Django flush instead of dropping database (safer, keeps structure)',
        )

    def handle(self, *args, **options):
        no_input = options.get('no_input', False)
        repopulate = options.get('repopulate', False)
        skip_migrations = options.get('skip_migrations', False)
        flush_only = options.get('flush_only', False)

        # Safety check
        if not no_input:
            self.stdout.write(self.style.ERROR(
                '\n⚠️  WARNING: This will DELETE ALL DATA in the database!'
            ))
            self.stdout.write(self.style.ERROR(
                'This action cannot be undone.\n'
            ))
            
            # Check if we're in production
            if not settings.DEBUG:
                self.stdout.write(self.style.ERROR(
                    '⚠️  DEBUG is False - this appears to be a production environment!'
                ))
                confirm = input('Type "DELETE ALL DATA" to confirm: ')
                if confirm != 'DELETE ALL DATA':
                    self.stdout.write(self.style.WARNING('Reset cancelled.'))
                    return
            else:
                confirm = input('Are you sure you want to reset the database? (yes/no): ')
                if confirm.lower() not in ['yes', 'y']:
                    self.stdout.write(self.style.WARNING('Reset cancelled.'))
                    return

        self.stdout.write(self.style.SUCCESS('Starting database reset...'))

        # Option 1: Use Django flush (safer - keeps structure, deletes data)
        if flush_only:
            self.stdout.write(self.style.WARNING('Step 1/3: Flushing database (deleting all data)...'))
            try:
                call_command('flush', verbosity=1, interactive=False, noinput=True)
                self.stdout.write(self.style.SUCCESS('✓ Database flushed'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error flushing database: {e}'))
                return

            # Step 2: Run migrations (in case schema changed)
            if not skip_migrations:
                self.stdout.write(self.style.WARNING('Step 2/3: Running migrations...'))
                try:
                    call_command('migrate', verbosity=1, interactive=False)
                    self.stdout.write(self.style.SUCCESS('✓ Migrations completed'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error running migrations: {e}'))
                    return
            else:
                self.stdout.write(self.style.WARNING('Skipping migrations (--skip-migrations)'))

            # Step 3: Repopulate if requested
            if repopulate:
                self.stdout.write(self.style.WARNING('Step 3/3: Repopulating database...'))
                try:
                    call_command('setupdata', verbosity=1)
                    self.stdout.write(self.style.SUCCESS('✓ Database repopulated'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error repopulating database: {e}'))
            else:
                self.stdout.write(self.style.WARNING('Skipping repopulation (use --repopulate to enable)'))

            # Summary
            self.stdout.write(self.style.SUCCESS('\n✅ Database reset complete!'))
            self.stdout.write(self.style.SUCCESS('\n📝 Next Steps:'))
            if not repopulate:
                self.stdout.write('  1. Run: python manage.py setupdata (to populate initial data)')
                self.stdout.write('  2. Run: python manage.py createsuperuser (to create admin user)')
                self.stdout.write('  3. Run: python manage.py add_business_owner (to add business owner)')
            else:
                self.stdout.write('  1. Run: python manage.py add_business_owner (to add business owner)')
                self.stdout.write('  2. Update API keys in integration settings')
            self.stdout.write('')
            return

        # Option 2: Drop and recreate database (complete reset)
        # Determine database type
        db_engine = settings.DATABASES['default']['ENGINE']
        db_name = settings.DATABASES['default']['NAME']

        try:
            if 'sqlite' in db_engine:
                # SQLite: Delete the database file
                self.stdout.write(self.style.WARNING('Step 1/4: Dropping SQLite database...'))
                db_path = settings.DATABASES['default']['NAME']
                if os.path.exists(db_path):
                    os.remove(db_path)
                    self.stdout.write(self.style.SUCCESS(f'✓ Deleted database file: {db_path}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Database file not found: {db_path}'))

            elif 'mysql' in db_engine:
                # MySQL: Drop and recreate database
                self.stdout.write(self.style.WARNING('Step 1/4: Dropping MySQL database...'))
                db_user = settings.DATABASES['default']['USER']
                db_password = settings.DATABASES['default']['PASSWORD']
                db_host = settings.DATABASES['default']['HOST']
                db_port = settings.DATABASES['default'].get('PORT', '3306')

                # Try pymysql first, then mysql.connector
                mysql_connection = None
                try:
                    import pymysql
                    mysql_connection = pymysql.connect(
                        host=db_host,
                        port=int(db_port),
                        user=db_user,
                        password=db_password,
                    )
                except ImportError:
                    try:
                        import mysql.connector
                        mysql_connection = mysql.connector.connect(
                            host=db_host,
                            port=int(db_port),
                            user=db_user,
                            password=db_password,
                        )
                    except ImportError:
                        self.stdout.write(self.style.ERROR(
                            'MySQL driver not found. Install pymysql or mysql-connector-python.'
                        ))
                        self.stdout.write(self.style.WARNING(
                            'Please manually drop and recreate the database, then run migrations.'
                        ))
                        return

                if mysql_connection:
                    try:
                        with mysql_connection.cursor() as cursor:
                            # Drop database
                            cursor.execute(f'DROP DATABASE IF EXISTS `{db_name}`')
                            self.stdout.write(self.style.SUCCESS(f'✓ Dropped database: {db_name}'))
                            
                            # Create database
                            cursor.execute(f'CREATE DATABASE `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
                            self.stdout.write(self.style.SUCCESS(f'✓ Created database: {db_name}'))
                        
                        mysql_connection.commit()
                    finally:
                        mysql_connection.close()

            elif 'postgresql' in db_engine or 'postgis' in db_engine:
                # PostgreSQL: Drop and recreate database
                self.stdout.write(self.style.WARNING('Step 1/4: Dropping PostgreSQL database...'))
                try:
                    import psycopg2
                    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
                except ImportError:
                    self.stdout.write(self.style.ERROR(
                        'psycopg2 not found. Install psycopg2-binary or psycopg2.'
                    ))
                    self.stdout.write(self.style.WARNING(
                        'Please manually drop and recreate the database, then run migrations.'
                    ))
                    return
                
                db_user = settings.DATABASES['default']['USER']
                db_password = settings.DATABASES['default']['PASSWORD']
                db_host = settings.DATABASES['default']['HOST']
                db_port = settings.DATABASES['default'].get('PORT', '5432')

                # Connect to postgres database (not the specific database)
                conn = psycopg2.connect(
                    host=db_host,
                    port=db_port,
                    user=db_user,
                    password=db_password,
                    database='postgres'  # Connect to default postgres database
                )
                conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

                try:
                    with conn.cursor() as cursor:
                        # Terminate existing connections
                        cursor.execute(f"""
                            SELECT pg_terminate_backend(pg_stat_activity.pid)
                            FROM pg_stat_activity
                            WHERE pg_stat_activity.datname = '{db_name}'
                            AND pid <> pg_backend_pid();
                        """)
                        
                        # Drop database
                        cursor.execute(f'DROP DATABASE IF EXISTS "{db_name}"')
                        self.stdout.write(self.style.SUCCESS(f'✓ Dropped database: {db_name}'))
                        
                        # Create database
                        cursor.execute(f'CREATE DATABASE "{db_name}"')
                        self.stdout.write(self.style.SUCCESS(f'✓ Created database: {db_name}'))
                finally:
                    conn.close()

            else:
                self.stdout.write(self.style.ERROR(
                    f'Unsupported database engine: {db_engine}'
                ))
                self.stdout.write(self.style.WARNING(
                    'Please manually drop and recreate the database, then run migrations.'
                ))
                return

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error resetting database: {e}'))
            self.stdout.write(self.style.WARNING(
                'You may need to manually drop and recreate the database.'
            ))
            return

        # Step 2: Close Django database connection
        self.stdout.write(self.style.WARNING('Step 2/4: Closing database connections...'))
        connection.close()
        self.stdout.write(self.style.SUCCESS('✓ Connections closed'))

        # Step 3: Run migrations
        if not skip_migrations:
            self.stdout.write(self.style.WARNING('Step 3/4: Running migrations...'))
            try:
                call_command('migrate', verbosity=1, interactive=False)
                self.stdout.write(self.style.SUCCESS('✓ Migrations completed'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error running migrations: {e}'))
                return
        else:
            self.stdout.write(self.style.WARNING('Skipping migrations (--skip-migrations)'))

        # Step 4: Repopulate if requested
        if repopulate:
            self.stdout.write(self.style.WARNING('Step 4/4: Repopulating database...'))
            try:
                # Run setupdata to populate initial data
                call_command('setupdata', verbosity=1)
                self.stdout.write(self.style.SUCCESS('✓ Database repopulated'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error repopulating database: {e}'))
                self.stdout.write(self.style.WARNING(
                    'You may need to manually run: python manage.py setupdata'
                ))
        else:
            self.stdout.write(self.style.WARNING('Skipping repopulation (use --repopulate to enable)'))

        # Summary
        self.stdout.write(self.style.SUCCESS('\n✅ Database reset complete!'))
        self.stdout.write(self.style.SUCCESS('\n📝 Next Steps:'))
        if not repopulate:
            self.stdout.write('  1. Run: python manage.py setupdata (to populate initial data)')
            self.stdout.write('  2. Run: python manage.py createsuperuser (to create admin user)')
            self.stdout.write('  3. Run: python manage.py add_business_owner (to add business owner)')
        else:
            self.stdout.write('  1. Run: python manage.py add_business_owner (to add business owner)')
            self.stdout.write('  2. Update API keys in integration settings')
        
        self.stdout.write('')

