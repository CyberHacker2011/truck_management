@echo off
echo ========================================
echo Truck Management System - Setup Script
echo ========================================
echo.

echo Step 1: Installing dependencies...
pipenv install
if %errorlevel% neq 0 (
    echo Error installing dependencies!
    pause
    exit /b 1
)

echo.
echo Step 2: Running database migrations...
cd truck_management
pipenv run python manage.py makemigrations
pipenv run python manage.py migrate
if %errorlevel% neq 0 (
    echo Error running migrations!
    cd ..
    pause
    exit /b 1
)

echo.
echo Step 3: Creating superuser...
echo Please enter superuser credentials when prompted:
pipenv run python manage.py createsuperuser

echo.
echo Step 4: Populating sample data...
pipenv run python manage.py populate_sample_data

cd ..

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo To start the server, run:
echo   cd truck_management
echo   pipenv run python manage.py runserver
echo.
echo Then access:
echo   - API: http://localhost:8000/api/
echo   - Admin: http://localhost:8000/admin/
echo   - API Docs: http://localhost:8000/api/docs/
echo.
pause
