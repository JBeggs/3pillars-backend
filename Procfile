release: mkdir -p media/locks staticfiles && python run_migrations.py && python manage.py collectstatic --noinput
web: gunicorn webcrm.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 30 --graceful-timeout 10 --max-requests 1000 --max-requests-jitter 100

