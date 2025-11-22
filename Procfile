release: mkdir -p media/locks staticfiles && python manage.py migrate && python manage.py collectstatic --noinput
web: gunicorn webcrm.wsgi:application --bind 0.0.0.0:$PORT

