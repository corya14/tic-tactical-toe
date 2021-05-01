FROM ubuntu:latest
ENV DEBIAN_FRONTEND noninteractive
ENV DISPLAY :1

RUN apt update && apt install -y \
   python3 \
   python3-venv \
   python3-pip

RUN mkdir /app

COPY requirements.txt /app
COPY localhost-TEST.crt /app
COPY localhost-TEST.key /app
COPY ticTacticalToe /app/ticTacticalToe
COPY accounts /app/accounts
COPY game /app/game
COPY stats /app/stats
COPY static /app/static
COPY templates /app/templates
COPY manage.py /app
RUN mkdir -p /app/logs

WORKDIR /app

ENV DJANGO_SETTINGS_MODULE=ticTacticalToe.production
ARG DJANGO_SECRET_KEY
ENV SECRET_KEY=$DJANGO_SECRET_KEY

RUN pip3 install -r requirements.txt
RUN python3 manage.py makemigrations
RUN python3 manage.py migrate
RUN python3 manage.py collectstatic --noinput --clear

CMD ["daphne", "-e", "ssl:443:privateKey=localhost-TEST.key:certKey=localhost-TEST.crt", "ticTacticalToe.asgi:application"]
