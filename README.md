# vc-python

This is a simple Python implementation of a security camera and an API server that the camera and a web client can both access using standard REST APIs.

The security camera has two threads: one thread is generating event log every 10 seconds. The other thread is polling the API server (refresh every 60 seconds) until there's a web client request coming in. The camera will then send the log to the API server in another HTTP request.

REST API server:
1. '/', methods=['GET']: serving camera polling
2. '/verkada/api/v1.0/logs', methods=['GET']: web client requesting for camera event logs
3. '/verkada/api/v1.0/logs/post', methods=['POST']: camera posting/relaying event logs to API server

Implementation choices:

I used two queues for API server to facilitate relaying of camera event logs upon request of web client: 'request_queue' to keep track of incoming web client request and 'camera_response_queue' to keep track of incoming event log response from camera. 
The camera will open a request to API server every 60 seconds. If there is a web client request, 'request_queue' gets populated (with corresponding timestamp). Request session between API server and camera gets unblocked by retrieving the request from 'request_queue' and notify Camera. Camera then send the event logs to API server in a separate HTTP POST request. 'camera_response_queue' gets populated with the event logs from camera upon receiving the POST request, and unblocks and return the web client's synchronous rest call for event logs.

Instructions to run:

1. docker-compose build
2. bring up API server: docker-compose up server 
3. bring up security camera: docker-compose up camera
4. make web client request to retrieve camera logs: 
	curl -i http://127.0.0.1:5000/verkada/api/v1.0/logs

Future improvement and concerns:

1. simultaneous web client request camera logs:

	It's possible that there are multiple web client requesting logs simultaneously. The camera has no open ports or server, it can only make an outgoing HTTP request to communicate with the API server. If there are multiple web client request arrived within the timeframe of camera sending event logs back to API server for the first web client request, the 'request_queue' will queue all the incoming requests. The camera served the response for the first request with a POST request, and then re-establish the connection with the API server, get the next request in 'request_queue' (depending on queue implementation: Queue, LifoQueue, or PriorityQueue), immediately follows with another POST request to serve the next web client request, until all the requests in 'request_queue' are served. There will be NO race condition, due to the fact that camera to API server is one-way street. 

2. API server supports multiple cameras:

	A natural extension to this is that the API server can server more than one camera (potentially really large number of cameras). A simple solution is to maintain two HashMap of queues: <{cameraId}, {request_queue}> and <{cameraId}, {camera_response_queue}>, this is, each camera has two queues: one for web client request and one for camera event log response.

	The rest APIs will be:

	/verkada/api/v1.0/logs/{cameraId}
	/verkada/api/v1.0/logs/post/{cameraId}

	We can probably use other concurrency/parallelism mechanism of Python: condition variables for example. Also we can deploy the API server to Kubernetes cluster, to auto or manual scale up the number of pods to serve cameras and web client requests. 

3. camera log persistence and query by time range:

	The current implementation just stores all the event logs on camera (in-memory). We should be able to persist the camera logs into db. Camera itself can be associated with db to periodically persist log data, or it can be handled by API server. We should be able to support query by time range (for example: between timestamp1 and timestamp2, or after timestamp3). If no real-time persistence of all camera logs (that is, more recent logs still only reside on camera), we should be able to handle query range by possibly combining in-memory camera logs and persisted logs.

4. unit test: I should have included unit test, Unfortunately, I had to skip it with a full time job and family visit this weekend. 

Note: I am a newbie for Python language, but I enjoyed the learning process :).






