#!/bin/sh

set -e

echo "Apply database migrations"
python manage.py migrate

echo "Collect static files"
python manage.py collectstatic --noinput

echo "Starting Gunicorn"
exec gunicorn fitcal.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers=2 \
    --threads=2 \
    --timeout=30 \
    --access-logfile - \
    --error-logfile -
