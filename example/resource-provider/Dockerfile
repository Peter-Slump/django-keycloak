FROM python:3.7-alpine

RUN apk update \
   && apk add git openssl-dev libffi-dev python-dev build-base

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

EXPOSE 8001

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8001" ]
