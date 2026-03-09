# SYSTEM DESCRIPTION:

Mars Habitat Control is an integrated IoT platform designed to monitor and automate environmental conditions within a simulated Martian habitat. The system acquires heterogeneous telemetry via REST protocols and SSE streams, normalizes the data into a single standard format to power an automation rules engine and a real-time web dashboard, while simultaneously allowing for both automatic and manual control of actuators.

# CONTAINERS:

## CONTAINER_NAME: rest-poller

### DESCRIPTION: 
This container is dedicated to the cyclic polling of the simulator's REST endpoints for discrete environmental sensors. It ensures that low-frequency data is constantly updated.

### PORTS: 
None

### PERSISTENCE EVALUATION
This container does not require data persistence. It operates exclusively on transient data in memory that is immediately forwarded to the Broker.

### EXTERNAL SERVICES CONNECTIONS
Connects to the Simulator microservice via HTTP for data retrieval and to the ActiveMQ microservice via the STOMP protocol for publication.

### MICROSERVICES:

#### MICROSERVICE: rest-poller
- TYPE: backend
- DESCRIPTION: Python service that executes scheduled GET requests to the simulator.
- PORTS: none
- TECHNOLOGICAL SPECIFICATION:
Developed in Python 3.12-slim. It uses the `requests` library for HTTP polling and `stomp.py` for asynchronous integration with the message broker.
- SERVICE ARCHITECTURE: 
The service implements an infinite loop that, every 5 seconds, iterates over a list of predefined sensors, retrieves the raw JSON, calls the `normalizer.py` module for transformation, and publishes the result to the `mars_telemetry` queue.

- ENDPOINTS: 
		
	| HTTP METHOD | URL | Description |
	| ----------- | --- | ----------- |
    | GET | /api/sensors/{sensor_id} | Retrieves the latest value for a specific environmental sensor |

## CONTAINER_NAME: stream-subscriber

### DESCRIPTION:
A specialized container for handling persistent HTTP connections (Server-Sent Events) to capture high-frequency technical telemetry produced by the simulator.

### PORTS: 
None

### PERSISTENCE EVALUATION
No local persistence required. Data is transformed "on-the-fly" and published to the Broker.

### EXTERNAL SERVICES CONNECTIONS
Persistent connection to the Simulator (HTTP Streaming) and STOMP connection to the Broker.

### MICROSERVICES:

#### MICROSERVICE: stream-subscriber
- TYPE: backend
- DESCRIPTION: SSE data stream manager for real-time telemetry.
- PORTS: none
- TECHNOLOGICAL SPECIFICATION:
Python 3.12-slim with support for HTTP streaming. It utilizes `normalizer.py` to map `topic.power.v1` and `topic.environment.v1` contracts.
- SERVICE ARCHITECTURE: 
The service initiates separate threads for each telemetry topic (e.g., radiation, solar_array). Each thread maintains an open connection with the simulator, decodes incoming data chunks, and forwards them to the broker after normalization.

- ENDPOINTS: 

	| HTTP METHOD | URL | Description |
	| ----------- | --- | ----------- |
    | GET | /api/telemetry/stream/{topic} | Subscription to the SSE stream for a specific technical topic |

## CONTAINER_NAME: actuator-executor

### DESCRIPTION: 
Acts as the system's actuation bridge. It is a pure consumer that waits for instructions from the broker to translate them into physical actions on the simulator.

### PORTS: 
None

### PERSISTENCE EVALUATION
No persistence required. The container is stateless.

### EXTERNAL SERVICES CONNECTIONS
STOMP connection to the Broker for command reception and POST requests to the Simulator for execution.

### MICROSERVICES:

#### MICROSERVICE: actuator-executor
- TYPE: backend
- DESCRIPTION: STOMP consumer for executing commands toward the actuators.
- PORTS: none
- TECHNOLOGICAL SPECIFICATION:
Developed in Python 3.12-slim. It uses `stomp.py` to listen to the `actuator_command` queue.
- SERVICE ARCHITECTURE: 
The service implements a `ConnectionListener` that waits for JSON messages on the queue. Upon receiving a command (e.g., `{"id": "cooling_fan", "action": "ON"}`), it performs a REST POST call to the simulator.

- ENDPOINTS: 

	| HTTP METHOD | URL | Description |
	| ----------- | --- | ----------- |
    | POST | /api/actuators/{id} | Sends the state change command to the specific actuator in the simulator |

## CONTAINER_NAME: activemq

### DESCRIPTION: 
The messaging backbone of the platform. It manages the asynchronous routing of data between the Ingestion microservices, the Automation Engine, and the Frontend.

### PORTS: 
61613 (STOMP), 8161 (Web Console)

### PERSISTENCE EVALUATION
Configured for transient messaging. It is not used as a historical archive in this project.

### EXTERNAL SERVICES CONNECTIONS
No external connections.

### MICROSERVICES:

#### MICROSERVICE: activemq
- TYPE: middleware
- DESCRIPTION: STOMP broker based on Apache ActiveMQ Classic.
- PORTS: 61613, 8161
- TECHNOLOGICAL SPECIFICATION:
Docker image `apache/activemq-classic:latest`.
- SERVICE ARCHITECTURE: 
Manages queues (`actuator_command`) and topics (`mars_telemetry`) for service decoupling.