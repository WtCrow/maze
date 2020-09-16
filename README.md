#Maze for a while.

You can see result to this url: https://maze-for-a-while.herokuapp.com/

If you want start this project local:

1) Start redis-server (easy path with docker: `sudo docker run -p 6379:6379 -d redis:5`)
2) Enter in terminal: `cd /project/path`
3) Enter in terminal: `pip install -r requirements.txt`
4) Create empty database
5) Define next env variable:
- SECRET_KEY
- DB_ENGINE
- DB_NAME
- DB_USER
- DB_PASSWORD
- DB_HOST
- DB_PORT
6) Create migration: `python manage.py makemigrations game`
7) Applying migrations: `python manage.py migrate`
8) Start `python manage.py runserver` or `daphne maze.asgi:application --port 8000 --bind localhost`
9) go to url http://localhost:8000/
10) Profit!
