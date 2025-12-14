#!/bin/bash

# Run database migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start gunicorn
echo "Starting server..."
exec gunicorn retirement_planner.wsgi:application --bind 0.0.0.0:$PORT
