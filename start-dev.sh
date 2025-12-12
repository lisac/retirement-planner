#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Start Django in background
python manage.py runserver &
DJANGO_PID=$!

# Start Tailwind
python manage.py tailwind start

# When Tailwind stops (Ctrl+C), also stop Django
kill $DJANGO_PID