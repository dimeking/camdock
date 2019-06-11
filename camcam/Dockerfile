FROM ubuntu:latest
MAINTAINER Hari Raja "harihraja@gmail.com"

# CAMCAM
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update
RUN apt-get install -y python3 python3-dev python3-pip nginx tzdata
RUN pip3 install uwsgi

COPY . ./app
WORKDIR ./app
RUN pip3 install -r requirements.txt

# Set the locale
ENV LANG C.UTF-8  
ENV LC_ALL C.UTF-8 

# Set the timezone
RUN ln -fs /usr/share/zoneinfo/US/Pacific /etc/localtime
RUN dpkg-reconfigure -f noninteractive tzdata

COPY ./nginx.conf /etc/nginx/sites-enabled/default
CMD service nginx start && uwsgi -s /tmp/uwsgi.sock --chmod-socket=666 --manage-script-name --mount /=app:app

RUN export FLASK_APP=app.py
CMD ["flask", "run", "--host", "0.0.0.0"]
