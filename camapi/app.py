"""
author: Hari Raja
email: harihraja@gmail.com
---------------------------------
A camera API server made with Flask.
---------------------------------
MIT license.
"""

# create flask app
from flask import Flask
from flask import request
import flask, json
app = Flask(__name__)

# virtual camera service name hardcoded for now
# TODO::Discovery mechanism 
# CAM_API_SERVER = 'http://localhost:5000'
CAM_API_SERVER = 'http://docker-machine.hr:5000'
APP_NAME = 'CamAPI'

# API Tags
API_ERROR_TAG = 'error'
API_ACTION_TAG = 'action'
API_TYPE_TAG = 'type'
API_ID_TAG = 'ID'
API_MESSAGE_TAG = 'message'
API_EVENT_TIME_TAG = 'event_time'
API_EVENT_MESSAGE_TAG = 'event_message'
API_LISTEN_CAM_TAG = 'listen_cam'
API_LOG_CAM_TAG = 'log_cam'

#
# setup log handler and app logger
#
import logging
from io import StringIO
from logging import Formatter, StreamHandler
# from logging.handlers import MemoryHandler

log_stream = StringIO()
handler = StreamHandler(log_stream)
handler.setLevel(logging.INFO)
handler.setFormatter(Formatter('%(message)s'))
# TODO: limit memory log size & flush at exit
# memoryhandler = MemoryHandler(1024*100, logging.INFO, handler)

app.logger.setLevel(logging.INFO)
app.logger.addHandler(handler)  

#
# threading events
#
from threading import Event, Lock
listen_log_events = {}

def get_listen_cam_event(id):
    if id not in listen_log_events.keys():
        listen_log_events[id] = {API_LISTEN_CAM_TAG: Event(), API_LOG_CAM_TAG: Event()}
    return listen_log_events[id][API_LISTEN_CAM_TAG]

def get_log_cam_event(id):
    if id not in listen_log_events.keys():
        listen_log_events[id] = {API_LISTEN_CAM_TAG: Event(), API_LOG_CAM_TAG: Event()}
    return listen_log_events[id][API_LOG_CAM_TAG]


#
# routes
#
@app.route('/')
def index():
    return APP_NAME

@app.route('/listen')
def listen():
    id = request.args.get(API_ID_TAG) if API_ID_TAG in request.args else None
    if id is None:
        return flask.jsonify({API_ERROR_TAG : 'args'})

    # wait for listen event 
    get_listen_cam_event(id).wait()
    get_listen_cam_event(id).clear()

    #inform virtual cam service to post log
    return flask.jsonify({API_ACTION_TAG : 'logcam', API_TYPE_TAG : 'POST'})

@app.route('/logcam', methods=['POST'])
def logcam():
    
    with Lock():
        # read the log to append it 
        camera_event_logs = []
        if len(log_stream.getvalue()) > 0:
            try:
                camera_event_logs = json.loads(log_stream.getvalue())
            except ValueError as e:
                camera_event_logs = []
            finally:
                log_stream.truncate(0)
                log_stream.seek(0)
        
        # save the log
        camera_events = request.get_json()
        camera_event_logs.append(camera_events)
        app.logger.info(json.dumps(camera_event_logs))

        # indicate log is ready
        id = camera_events[API_ID_TAG]
        get_log_cam_event(id).set()

    return flask.jsonify({'result' : 'success'})

@app.route('/logs')
def logs():
    camera_event_logs = []
    with Lock():
        # signal event
        for id in listen_log_events.keys():
            app.logger.debug({id: 'set listen event'})
            get_listen_cam_event(id).set() 

        # wait for the log event
        time_out = False
        for id in listen_log_events.keys():
            time_out = time_out or get_log_cam_event(id).wait(timeout=5.0)
            if not time_out:
                return flask.jsonify({API_ERROR_TAG: 'timeout'})  
            get_log_cam_event(id).clear()  


        # read the log & reset it
        memory_log = log_stream.getvalue()
        log_lines = memory_log.split('\n') if memory_log else []
        camera_event_logs = []

        try:
            for log_line in log_lines:
                camera_event_logs.append(json.loads(log_stream.getvalue()))
        except ValueError as e:
            camera_event_logs = []
        finally:
            log_stream.truncate(0)
            log_stream.seek(0)

    return flask.jsonify(camera_event_logs)

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

