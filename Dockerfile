FROM python:3.7-alpine
MAINTAINER William Lindholm

COPY ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

COPY ./juniordev /app/juniordev
COPY ./main      /app/main
COPY ./manage.py /app/manage.py
COPY ./status /app/status

WORKDIR /app

RUN adduser -D user
USER user
