#!flask/bin/python
import time
import random
import threading
import requests

event_type = [
        "detected motion",
        "user started viewing live video",
        "brightness adjusted",
        "camera reset"
    ]

events = []

endpoint_get = "http://server:5000/"
endpoint_post = "http://server:5000/verkada/api/v1.0/logs/post"


def generate_events():
    while True:
        generate_single_event()
        print(events)
        time.sleep(10)

def generate_single_event():
    print("generating new event")
    event = {
        'timestamp': time.time(),
        'description': random.choice(event_type)
    }
    events.append(event)

def send_logs():
    print("ready to send event log from camera")
    print(events)
    r = requests.post(url = endpoint_post, json = {'events' : events})
    response = r.text
    print("response after sending logs: %s" %response)

def camera_polling():
    print("before polling loop")
    while True:
        print("create a new request")

        pull_request = requests.get(endpoint_get).status_code == 200

        if pull_request:
            print("Sending logs from camera")
            send_logs()


def main():
    print("starting")
    threading.Timer(0, generate_events).start()
    threading.Timer(0, camera_polling).start()


if __name__ == "__main__":
    main()

