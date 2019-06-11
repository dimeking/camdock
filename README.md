CamDock
===========

A system using docker that consists of two containers:
    1. CamCam: Virtual camera, written in python (device)
    2. CamAPI: Python/flask HTTP API server (apiserver)
The virtual camera will not have any open ports for security reasons. As a result, it will only make requests out to the API server.

The API server is a web server that the camera and a web client can both access using standard REST APIs.

Requirements
------------

Ubuntu Droplet (Digital Ocean):
- Ensure cURL is available for testing
- Ensure Docker, Docker-Compose (Install Docker CE) is required for creating device & apiserver containers

OR

OSX:
- Ensure cURL is available for testing
- Ensure Docker, Docker-Compose (Install Docker CE) is required for creating device & apiserver containers
- Ensure Docker-Machine is required for running device & apiserver containers


Installation and Setup
------------------------

Ubuntu Droplet (Digital Ocean):
- Identify DROPLET_IP from Digital Ocean
- Copy CamDock to /home:
    $ rsync -avz ~/CamDock root@DROPLET_IP:/home/CamDock
    $ ssh root@DROPLET_IP
    $ cd /home/CamDock


OSX:
- Copy CamDock to $HOME:
    $ cd ~/CamDock
- Create a machine & setup:
	$ docker-machine create --driver virtualbox default
	$ docker-machine env default
	$ eval "$(docker-machine env default)"
 

Running CamCam (device) & CamAPI (apiserver)
--------------------------------------------

You can start both CamCam (device) & CamAPI (apiserver) docker containers and docker network with the following command:

    $ docker-compose up -d --scale device=4


Ubuntu Droplet (Digital Ocean):
   $ export CAMAPI_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' camdock_apiserver_1)
OSX:
   $ export CAMAPI_IP = $(docker-machine ip)


Ensure docker containers are up & running with following command:

    $ curl http://$CAMAPI_IP:5000/logs

View the logs from docker containers with following command:

    $ docker-compose logs

Shutting down 
-------------
You can unwind the docker containers with the following command:

    $ docker-compose down

You can remove the docker images, if you want as:

    $ docker image rm dimeking/camapi:latest dimeking/camcam:latest


Steps to deploy to Production  
-----------------------------

A. Configuration:

- Include and configure uwsgi
- configure nginx
- create startup scripts
- update FLASK_ENV in docker-compose.yml to production 

B. Deployment:

- Setup Docker Stack Deploy and Restart Policy

C. Testing:

- Use Digital Ocean or equivalent to deploy say 16 devices and 2 apiservers with load balancer