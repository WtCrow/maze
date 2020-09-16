#Maze for a while.

You can see result to this url: https://maze-for-a-while.herokuapp.com/

If you want start this project local:

1) Enter in terminal: `cd /project/path`
2) Enter in terminal: `pip install -r requirements.txt`
3) Create empty database
4) Define next env variable:
- SECRET_KEY
- DB_ENGINE
- DB_NAME
- DB_USER
- DB_PASSWORD
- DB_HOST
- DB_PORT
5) Create migration: `python manage.py makemigrations game`
6) Applying migrations: `python manage.py migrate`
7) Start `python manage.py runserver` or `daphne maze.asgi:application --port 8000 --bind localhost`
8) go to url http://localhost:8000/
9) Profit!
