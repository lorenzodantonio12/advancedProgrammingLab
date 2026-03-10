# SYSTEM DESCRIPTION:

Mars Habitat Control is an integrated IoT platform designed to monitor and automate environmental conditions within a simulated Martian habitat. The system acquires heterogeneous telemetry via REST protocols and SSE streams, normalizes the data into a single standard format to power an automation rules engine and a real-time web dashboard, while simultaneously allowing for both automatic and manual control of actuators.

---

### ARCHITECTURAL JUSTIFICATION: DECOUPLED INGESTION SERVICES

The Ingestion and Actuation logic has been intentionally distributed across three separate containers (`rest-poller`, `stream-subscriber`, and `actuator-executor`) instead of a single monolithic container. This architectural choice is based on these principles:

1.  **Fault Isolation and Reliability**: Each service handles a different communication protocol (REST Polling, SSE Streaming, and STOMP Consumption). By separating them, a network failure or a crash in the real-time streaming service (`stream-subscriber`) does not affect the environmental monitoring (`rest-poller`) or the ability to send commands (`actuator-executor`).
2.  **Scalability**: Discrete containers allow for independent scaling. If the number of REST sensors increases, more instances of the `rest-poller` can be deployed without wasting resources on additional streamers or executors.
3.  **Specific Resource Management**: The `stream-subscriber` maintains persistent connections which are memory-heavy, while the `rest-poller` is CPU-bound during its cyclic bursts. Separate containers allow Docker to manage and limit resources specifically for each task's needs.
4.  **Logging and Observability**: Decoupling the services provides clean, isolated log streams for each process, significantly simplifying debugging and system health monitoring during habitat operations.

---

# USER STORIES:

1) As a user, I want to view all the sensors and their live telemetry in a compact dashboard
2) As a user, I want to see clear visual status indicators for each sensor
3) As a user, I want to read the real-time values and unit of measurements for every metric
4) As a user, I want to view historical data charts for key metrics
5) As a user, I want to view the current state (ON/OFF) of every actuator
6) As a user, I want to manually toggle the state of the actuators
7) As a user, I want to be visually notified when an actuator changes state due to a rule
8) As a user, I want to see a dedicated page with a list of all active automation rules
9) As a user, I want to create a new rule
10) As a user, I want to modify the parameters of an existing rule
11) As a user, I want to delete a rule
12) As a user, I want all the rules to be saved automatically in a persistent database
13) As a user, I want the system to automatically block the creation of a new rule if its logic overlaps with an existing one
14) As a user, I want the system to automatically block the modification of a rule if the updated parameters conflict with another existing rule
15) As a user, I want to be visually notified when I create, modify or delete a rule

# CONTAINERS:

## CONTAINER_NAME: simulator (mars_simulator)

### DESCRIPTION: 
This container provides the simulated Mars habitat environment. It acts as the primary data source, exposing various sensor metrics via REST and SSE, and accepting state change commands for actuators.

### PORTS: 
8080:8080

### PERSISTENCE EVALUATION
The simulator acts as a runtime source of telemetry and transient actuator states; it does not manage persistent application data for the platform.

### EXTERNAL SERVICES CONNECTIONS
Standalone server that receives incoming HTTP requests from the ingestion and actuation containers and maintains persistent SSE connections.

### MICROSERVICES:

#### MICROSERVICE: simulator
- **TYPE**: IoT Simulator (External)
- **DESCRIPTION**: Docker image (`mars-iot-simulator:latest`) providing a realistic IoT simulation of a Martian base.
- **PORTS**: 8080
- **TECHNOLOGICAL SPECIFICATION**: Accessible via REST and SSE APIs using defined schema families (e.g., `rest.scalar.v1`, `topic.power.v1`).
- **SERVICE ARCHITECTURE**: Reactive data provider maintaining internal state for sensors and actuators.

- **ENDPOINTS (Exposed)**: 
		
	| HTTP METHOD | URL | Description | User Stories |
	| ----------- | --- | ----------- | ------------ |
    | GET | `/api/sensors` | Lists available REST sensors | 1 |
    | GET | `/api/sensors/{id}` | Returns the latest value for a specific sensor | 1, 3 |
    | GET | `/api/telemetry/topics` | Lists available SSE topics | 1 |
    | GET | `/api/telemetry/stream/{topic}` | Provides a persistent SSE stream for high-frequency metrics | 1, 2, 3 |
    | GET | `/api/actuators` | Lists all actuators and their current states | 5 |
    | POST | `/api/actuators/{id}` | Updates the state of a specific actuator | 6, 7 |

## CONTAINER_NAME: rest-poller

### DESCRIPTION: 
This container is dedicated to the cyclic polling of the simulator's REST endpoints for discrete environmental sensors. It ensures that low-frequency data is constantly updated.

### USER STORIES:
1, 2, 3

### PORTS: 
None

### PERSISTENCE EVALUATION
This container does not require data persistence. It operates exclusively on transient data in memory that is immediately forwarded to the Broker.

### EXTERNAL SERVICES CONNECTIONS
Connects to the Simulator microservice via HTTP for data retrieval and to the ActiveMQ microservice via the STOMP protocol for publication.

### MICROSERVICES:

#### MICROSERVICE: rest-poller
- **TYPE**: backend
- **DESCRIPTION**: Python service that executes scheduled GET requests to the simulator.
- **PORTS**: none
- **TECHNOLOGICAL SPECIFICATION**: Developed in Python 3.12-slim. It uses the `requests` library for HTTP polling and `stomp.py` for asynchronous integration with the message broker.
- **SERVICE ARCHITECTURE**: The service implements an infinite loop that, every 5 seconds, iterates over a list of predefined sensors, retrieves the raw JSON, calls the `normalizer.py` module for transformation, and publishes the result to the `mars_telemetry` queue.

- **CONSUMED EXTERNAL ENDPOINTS**:
        
    | HTTP METHOD | TARGET URL | Description | User Stories |
    | ----------- | --- | ----------- | ------------ |
    | GET | `/api/sensors/{sensor_id}` | Polls the latest value for environmental sensors (e.g., Temperature) | 1, 3 |

## CONTAINER_NAME: stream-subscriber

### DESCRIPTION:
A specialized container for handling persistent HTTP connections (Server-Sent Events) to capture high-frequency technical telemetry produced by the simulator.

### USER STORIES:
1, 2, 3

### PORTS: 
None

### PERSISTENCE EVALUATION
No local persistence required. Data is transformed "on-the-fly" and published to the Broker.

### EXTERNAL SERVICES CONNECTIONS
Persistent connection to the Simulator (HTTP Streaming) and STOMP connection to the Broker.

### MICROSERVICES:

#### MICROSERVICE: stream-subscriber
- **TYPE**: backend
- **DESCRIPTION**: SSE data stream manager for real-time telemetry.
- **PORTS**: none
- **TECHNOLOGICAL SPECIFICATION**: Python 3.12-slim with support for HTTP streaming. It utilizes `normalizer.py` to map incoming technical schemas (e.g., `solar_array`) to internal formats.
- **SERVICE ARCHITECTURE**: The service initiates separate threads for each telemetry topic. Each thread maintains an open connection with the simulator, decodes incoming data chunks, and forwards them to the broker after normalization.

- **CONSUMED EXTERNAL ENDPOINTS**: 

    | HTTP METHOD | TARGET URL | Description | User Stories |
    | ----------- | --- | ----------- | ------------ |
    | GET | `/api/telemetry/stream/{topic}` | Subscribes to live SSE technical topics (e.g., `solar_array`) | 1, 2 |

## CONTAINER_NAME: actuator-executor

### DESCRIPTION: 
Acts as the system's actuation bridge. It is a pure consumer that waits for instructions from the broker to translate them into physical actions on the simulator.

### USER STORIES:
5, 6, 7

### PORTS: 
None

### PERSISTENCE EVALUATION
No persistence required. The container is stateless.

### EXTERNAL SERVICES CONNECTIONS
STOMP connection to the Broker for command reception and POST requests to the Simulator for execution.

### MICROSERVICES:

#### MICROSERVICE: actuator-executor
- **TYPE**: backend
- **DESCRIPTION**: STOMP consumer for executing commands toward the actuators.
- **PORTS**: none
- **TECHNOLOGICAL SPECIFICATION**: Developed in Python 3.12-slim. It uses `stomp.py` to listen to the `actuator_command` queue.
- **SERVICE ARCHITECTURE**: The service implements a `ConnectionListener` that waits for JSON messages on the queue. Upon receiving a command, it performs a REST POST call to the simulator.

- **CONSUMED EXTERNAL ENDPOINTS**: 

    | HTTP METHOD | TARGET URL | Description | User Stories |
    | ----------- | --- | ----------- | ------------ |
    | POST | `/api/actuators/{id}` | Sends state updates (e.g., `{"state": "ON"}`) to the Simulator | 6, 7 |

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
- **TYPE**: middleware
- **DESCRIPTION**: STOMP broker based on Apache ActiveMQ Classic.
- **PORTS**: 61613, 8161
- **TECHNOLOGICAL SPECIFICATION**: Docker image `apache/activemq-classic:latest`.
- **SERVICE ARCHITECTURE**: Manages queues (`actuator_command`) and topics (`mars_telemetry`) for service decoupling.

## CONTAINER_NAME: automation-engine

### DESCRIPTION: 
This container acts as the central intelligence of the habitat. It manages the persistence of automation rules in a local database, evaluates incoming normalized sensor data against these rules in real-time, and provides a central API gateway for the frontend.

### USER STORIES:
8, 9, 10, 11, 12, 13, 14

### PORTS: 
8000:8000

### PERSISTENCE EVALUATION:
The container manages persistent data using an SQLite database named `mars_rules.db` to ensure that user-defined automation rules are preserved across container restarts.

### EXTERNAL SERVICES CONNECTIONS:
Establishes a STOMP connection to the ActiveMQ broker to subscribe to the telemetry topic (`mars_telemetry`) and send commands to the actuation topic (`actuator_command`). It exposes REST endpoints for communication with the `mars-frontend`.

### MICROSERVICES:

#### MICROSERVICE: automation-logic
- **TYPE**: backend
- **DESCRIPTION**: An event-driven API server and rules engine based on FastAPI.
- **PORTS**: 8000
- **TECHNOLOGICAL SPECIFICATION**: Developed in Python 3.12 using the FastAPI framework. It implements advanced interval-checking logic (`check_overlap`) to prevent conflicting rules.
- **SERVICE ARCHITECTURE**: The service follows a modular architecture:
    - **`main.py`**: Defines REST API endpoints.
    - **`automation_engine.py`**: Matches sensor events to rules and triggers actuator changes.
    - **`crud.py`**: Handles Create, Read, Update, and Delete operations for the SQLite database.
    - **`check_interval.py`**: Implements overlap detection for rule parameters.

- **ENDPOINTS**:
        
    | HTTP METHOD | URL | Description | User Stories |
    | ----------- | --- | ----------- | ------------ |
    | GET | `/api/get-rules` | Retrieves all automation rules from the database | 8 |
    | POST | `/api/create-rule` | Creates a new rule with anti-conflict validation | 9, 13 |
    | PATCH | `/api/update-rule/{id}` | Updates parameters of an existing rule with conflict checks | 10, 14 |
    | DELETE | `/api/delete-rule/{id}` | Permanently removes a rule from the system | 11 |

- **DB STRUCTURE**: 

    **_rules_** : | **_id_rule_** (PK) | sensor_name | operator | value | metric | actuator_name | state |

---

## CONTAINER_NAME: mars-frontend

### DESCRIPTION: 
Provides the interactive web interface for global habitat supervision. It enables real-time telemetry monitoring, historical trend visualization, and automation configuration.

### USER STORIES:
1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 15

### PORTS: 
8081:8081

### PERSISTENCE EVALUATION:
The frontend is stateless. Persistence is handled by the `automation-engine`.

### EXTERNAL SERVICES CONNECTIONS:
HTTP REST connection to the `automation-engine` and a STOMP connection to the ActiveMQ broker.

### MICROSERVICES:

#### MICROSERVICE: frontend-dashboard
- **TYPE**: frontend
- **DESCRIPTION**: A multi-page reactive dashboard built with NiceGUI.
- **PORTS**: 8081
- **TECHNOLOGICAL SPECIFICATION**: Developed in Python 3.12 with NiceGUI. It integrates Highcharts for time-series data visualization.
- **SERVICE ARCHITECTURE**: Organized into modular components and pages:
    - **`dashboard_page.py`**: Main monitoring layout.
    - **`rules_page.py`**: Full CRUD interface for automation rules.
    - **`components/`**: Reusable widgets for sensors, telemetry, and actuators.

- **PAGES**: 

    | Name | Description | Related Microservice | User Stories |
    | ---- | ----------- | -------------------- | ------------ |
    | Dashboard | Real-time sensor monitoring, technical telemetry, and actuator toggles | automation-logic | 1, 2, 3, 4, 5, 6, 7 |
    | Rules Engine | Management interface for automation rules with visual notifications | automation-logic | 8, 9, 10, 11, 15 |