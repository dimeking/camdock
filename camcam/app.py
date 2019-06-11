"""
author: Hari Raja
email: harihraja@gmail.com
---------------------------------
A simple virtual camera made with Flask.
---------------------------------
MIT license.
"""

from flask import Flask
import time, random, string
# create flask app
app = Flask(__name__)

# API server name hardcoded for now
# TODO::Discovery mechanism 
# API_SERVER = 'http://localhost:5000'
# API_SERVER = 'http://docker-machine.hr:5000'
API_SERVER = 'http://apiserver:5000'
APP_NAME = 'CamCam'
# 6 char random string
APP_ID = ''.join(random.SystemRandom(). \
choice(string.ascii_uppercase + string.digits) for _ in range(6))

# API Tags
API_ERROR_TAG = 'error'
API_ACTION_TAG = 'action'
API_TYPE_TAG = 'type'
API_ID_TAG = 'ID'
API_EVENTS_TAG = 'events'
API_EVENT_TIME_TAG = 'event_time'
API_EVENT_MESSAGE_TAG = 'event_message'

#
# setup log handler and app logger
#
import logging
from io import StringIO
from logging import Formatter, StreamHandler
# from logging.handlers import MemoryHandler

LOG_INTERVAL = 10
log_stream = StringIO()
handler = StreamHandler(log_stream)
handler.setLevel(logging.INFO)
handler.setFormatter(Formatter('%(asctime)s::%(message)s'))
# TODO: limit memory log size & flush at exit
# memoryhandler = MemoryHandler(1024*100, logging.INFO, handler)

app.logger.setLevel(logging.INFO)
app.logger.addHandler(handler)  

app.logger.info("virtual cam started")

# random event logging
import random

def log_random_event():
    random_events = [
        "detected motion at 16:30", 
        "user started viewing live video",
        "brightness adjusted +10",
        "camera moved left",
        "camera froze",
        "network connection lost"    
        ]
    random_index = random.randint(0, len(random_events)-1)
    log_message = random_events[random_index]
    app.logger.info(log_message)
    return log_message

#
# background scheduler
#
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

scheduler = BackgroundScheduler()
scheduler.add_job(func=log_random_event, trigger="interval", seconds=LOG_INTERVAL)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())



#
# call to api server
#
import requests
RECONNECT_INTERVAL = 60

def listen_api_server():
    listen_url = API_SERVER+'/listen?'+API_ID_TAG+'='+APP_ID
    try:
        # reconnect after 1min
        response = requests.get(listen_url, timeout=(5, 60))
    except requests.ConnectionError as e:
        return {API_ERROR_TAG : 'connection failure'}
    except requests.Timeout:
        return {API_ERROR_TAG : 'timeout failure'}

    return response.json()

def log_api_server(log_url):
    log_url = API_SERVER+'/'+log_url
    
    # read log messages 
    memory_log = log_stream.getvalue()
    log_lines = memory_log.split('\n') if memory_log else []
    events = []
    for log_line in log_lines:
        event = log_line.split('::')
        if len(event) > 1:
            events.append({API_EVENT_TIME_TAG: event[0], API_EVENT_MESSAGE_TAG: event[1]})

    try:
        response = requests.post(log_url, json={API_ID_TAG: APP_ID, API_EVENTS_TAG: events}, timeout=(5, 10))
    except requests.ConnectionError as e:
        return {API_ERROR_TAG : 'connection failure'}
    except requests.Timeout:
        return {API_ERROR_TAG : 'timeout failure'}

    return response.json()

def call_api_server():
    # listen, log and then listen
    delay = 1
    while True:
        res = listen_api_server()
        if (API_ERROR_TAG in res.keys()):
            # exponential backoff for connection errors but not timeout
            delay = 1 if 'timeout' in res[API_ERROR_TAG] else delay*2  
            time.sleep(delay)
            continue

        if (API_ACTION_TAG not in res.keys()):
            continue
        res = log_api_server(res[API_ACTION_TAG])
        if (API_ERROR_TAG in res.keys()):
            break

call_api_server()

#
# no routes
#

#
# error handlers
#

@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500

# run flask app
if __name__ == '__main__':  
    app.run(host='0.0.0.0')
