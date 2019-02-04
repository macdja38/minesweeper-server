FROM python:3-onbuild

RUN mkdir /code
WORKDIR /code

COPY requirements.txt /code
RUN pip install --no-cache-dir -r requirements.txt

COPY . /code

EXPOSE 8000

CMD ["gunicorn", "minesweeperserver.wsgi:application", "--bind=0.0.0.0:8000", "--workers=4"]
