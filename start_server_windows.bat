@echo off
IF EXIST venv (
echo venv exists...
) ELSE (
echo Creating venv...
python -m venv venv
echo Venv installed...
)
call .\\venv\\Scripts\\activate.bat

python manage.py makemigrations
python manage.py migrate
python manage.py runserver
