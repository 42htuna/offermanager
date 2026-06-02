#!/bin/bash
#python manage.py runserver 0.0.0.0:8000 --insecure
gunicorn offermanager.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 90
#Windows ortamı için en iyi alternatif "waitress"
#waitress-serve --port=8000 offermanager.wsgi:application
