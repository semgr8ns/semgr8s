FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY app.py /app

#CMD gunicorn --certfile=/app/cert.pem --keyfile=/app/key.pem --log-level=debug -bind 0.0.0.0:5000 app:app
CMD python app.py
