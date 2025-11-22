release: mkdir -p media/locks staticfiles && python run_migrations.py && python manage.py collectstatic --noinput
web: gunicorn webcrm.wsgi:application --bind 0.0.0.0:$PORT

