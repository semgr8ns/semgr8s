FROM python:3-alpine

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY semgr8s/ /app/semgr8s

CMD python -m semgr8s
