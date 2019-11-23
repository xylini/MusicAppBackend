if [[ ! -d "venv" ]]; then
    echo Creating virtualenv...
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate
python manage.py runserver