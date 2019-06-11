FROM ubuntu:latest
MAINTAINER Hari Raja "harihraja@gmail.com"

# CAMAPI
RUN apt-get update
RUN apt-get install -y python3 python3-dev python3-pip nginx
RUN pip3 install uwsgi
COPY . ./app
WORKDIR ./app
RUN pip3 install -r requirements.txt

# Set the locale
ENV LANG C.UTF-8  
ENV LC_ALL C.UTF-8 

COPY ./nginx.conf /etc/nginx/sites-enabled/default
CMD service nginx start && uwsgi -s /tmp/uwsgi.sock --chmod-socket=666 --manage-script-name --mount /=app:app

RUN export FLASK_APP=app.py
EXPOSE 5000
CMD ["flask", "run", "--host", "0.0.0.0", "-p", "5000"]
