# SYSTEM DESCRIPTION:

Mars Habitat Control is an integrated IoT platform designed to monitor and automate environmental conditions within a simulated Martian habitat. The system acquires heterogeneous telemetry via REST protocols and SSE streams from a simulator, normalizes the data into a single standard format to power an automation rules engine and a real-time web dashboard. The platform ensures habitat safety by evaluating complex automation rules in real-time and allowing for both automatic and manual control of actuators through a centralized message broker.

# USER STORIES:

1) As the User, I want to see environmental REST sensor data (Temp, Humidity, CO2) updated automatically every 5 seconds.
2) As the User, I want to monitor technical telemetry streams (Radiation, Solar Array) in real-time via persistent SSE connections.
3) As the User, I want all data, regardless of the source, to be normalized with correct measurement units (e.g., °C, kW, uSv/h).
4) As the User, I want the system to clean sensor IDs by removing technical prefixes for a clear display on the dashboard.
5) As the User, I want to be able to send ON/OFF commands to simulated actuators manually from the dashboard.
6) As the User, I want to see confirmation in the system logs for every command executed by the actuators.
7) As the User, I want the system to automatically trigger actuators (e.g., cooling fans) when specific sensor thresholds are exceeded.
8) As the User, I want to visualize all active automation rules in a dedicated section of the dashboard.
9) As the User, I want to enable or disable specific automation rules without deleting them.
10) As the User, I want to visualize real-time charts for sensors to identify trends in the habitat's environment.
11) As the User, I want the dashboard to highlight dangerous conditions (warnings) in red for immediate identification.
12) As the User, I want to see the total count of active sensors, live telemetries, and active rules in a summary widget.
13) As the User, I want the system to remain functional and provide telemetry even if one of the ingestion components crashes (Fault Isolation).
14) As the User, I want all sensor data to be synchronized across the Automation Engine and the Frontend via a shared Message Broker.
15) As the User, I want to see the exact timestamp of the last received update for each sensor to ensure data freshness.