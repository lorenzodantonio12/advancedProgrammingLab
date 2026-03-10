# SYSTEM DESCRIPTION:

Mars Habitat Control is an all-in-one monitoring and automation platform designed to manage life-support conditions in a simulated Martian base. The system acts as an intelligent bridge between the habitat's environment and the crew, collecting vital data such as temperature, radiation levels, and oxygen status. It automatically processes this information to ensure safety, triggering systems when dangerous conditions arise, and provides a real-time visual dashboard for manual supervision.

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

# 3. Data Normalization

The system takes JSON payloads from 8 different models. A data normalization function process these payloads and turn them into a unified schema.

## 3.1 Normalized Schema (`StandardFormat`)

Every incoming data point is transformed into the following unified structure before being published to the Message Broker:

```json
{
  "id": "string",            // Cleaned unique identifier for the sensor (e.g., "radiation")
  "metric": "string",        // The specific metric name (used for dashboard widget mapping)
  "timestamp": "ISO8601",    // Precision acquisition time generated during normalization
  "value": "number",         // Floating-point measurement value
  "unit": "string | null",   // Normalized unit of measurement (e.g., "°C", "kW", "uSv/h")
  "origin": "string",        // The schema family or source protocol (e.g., "rest.scalar.v1")
  "status": "string | null"  // Current status reported by the source (e.g., "OK", "WARNING")
}
```

## 3.2 Automation Rule Schema (`AutomationRule`)

To maintain consistency between data ingestion and system response, automation rules are defined using a schema that directly maps to the normalized sensor data. This allows the Rule Engine to evaluate conditions against the standardized telemetry:

```json
{
  "id_rule": "integer | null",   // Unique identifier for persistent storage (SQLite)
  "sensor_name": "string",       // Normalized sensor ID to monitor (e.g., "greenhouse_temperature")
  "metric": "string",            // The specific metric name to evaluate
  "operator": "string",          // Comparison logic: "<", "<=", "=", ">", ">="
  "value": "number",             // The threshold value for comparison
  "actuator_name": "string",     // Target actuator to be commanded (e.g., "cooling_fan")
  "state": "string"              // Target state to set: "ON" or "OFF"
}
```