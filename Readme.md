# About

This is the server-side of a Web based Minesweeper clone
It will bind to port 8000

# Setup

### Setup env

Copy `.env.example` to `.env` and change the secret.

### Enter virtual env

##### Linux / macos
`source env/bin/activate` 
##### Windows
`env\Scripts\activate`

### Install dependencies

`pip install -r requirements.txt`

### Setup Database

python manage.py migrate --run-syncdb

### Run Tests

python manage.py test

### Start dev server

python manage.py runserver