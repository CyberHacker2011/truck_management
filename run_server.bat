@echo off
echo Starting Truck Management System server...
cd truck_management
pipenv run python manage.py runserver
pause
