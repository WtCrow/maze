#Maze for a while.

If you want start this project:

1) Enter in terminal: `cd /project/path`
2) Enter in terminal: `pip install -r requirements.txt`
3) Define SECRET_KEY env variable
4) Create migration: `python manage.py makemigrations game`
5) Applying migrations: `python manage.py migrate`
6) (Optional) Create super user for django admin `django-admin createsuperuser`
7) Start `python manage.py runserver`
8) go to url http://localhost:8000/
9) Profit!
