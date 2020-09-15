#Maze for a while.

If you want start this project:

1) Start redis-server (easy path with docker: `sudo docker run -p 6379:6379 -d redis:5`)
1) Enter in terminal: `cd /project/path`
2) Enter in terminal: `pip install -r requirements.txt`
3) Define next env variable:
- SECRET_KEY
- REDIS_HOST
- REDIS_PORT
4) Create migration: `python manage.py makemigrations game`
5) Applying migrations: `python manage.py migrate`
6) Start `python manage.py runserver` or `daphne maze.asgi:application --port 8000 --bind localhost`
7) go to url http://localhost:8000/
8) Profit!
