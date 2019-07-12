#!flask/bin/python

from flask import Flask, jsonify, abort, request, make_response
import time
import queue

app = Flask(__name__)

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify( { 'error': 'Bad request' } ), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)

request_queue = queue.Queue()
camera_response_queue = queue.Queue()

@app.route('/')
def index():
    print('camera polling arrived')
    request_queue.get(block=True, timeout=60)
    return 'pull request initiated', 200

@app.route('/verkada/api/v1.0/logs', methods=['GET'])
def get_logs():
    request_queue.put(time.time())
    print("user request coming in")
    events = camera_response_queue.get(block=True)
    print("ready to send event log to user")
    return jsonify({'events': events})

@app.route('/verkada/api/v1.0/logs/post', methods=['POST'])
def retrieve_logs_from_camera():
    print(request.json)
    if not request.json:
        abort(400) 
    events = request.json.get('events')
    camera_response_queue.put(events)  
    print("retrieving event log from camera")
    return jsonify( { 'events': events } ), 201


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
