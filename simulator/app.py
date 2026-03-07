from flask import Flask, jsonify, request
import random
import time
import json

app = Flask(__name__)

@app.route('/api/sensors/<sensor_id>')
def get_sensor(sensor_id):
    # Simula dati per i sensori
    data = {
        "greenhouse_temperature": {"value": round(random.uniform(20.0, 30.0), 1), "unit": "°C"},
        "entrance_humidity": {"value": round(random.uniform(40.0, 60.0), 1), "unit": "%"},
        "co2_hall": {"value": round(random.uniform(400, 800), 0), "unit": "ppm"},
        "hydroponic_ph": {"value": round(random.uniform(5.5, 6.5), 2), "unit": ""},
        "water_tank_level": {"value": round(random.uniform(10, 100), 1), "unit": "%"},
        "corridor_pressure": {"value": round(random.uniform(980, 1020), 0), "unit": "hPa"},
        "air_quality_pm25": {"value": round(random.uniform(5, 25), 1), "unit": "µg/m³"},
        "air_quality_voc": {"value": round(random.uniform(50, 200), 0), "unit": "ppb"}
    }
    if sensor_id in data:
        return jsonify(data[sensor_id])
    return jsonify({"error": "Sensor not found"}), 404

@app.route('/api/actuators/<actuator_id>', methods=['POST'])
def set_actuator(actuator_id):
    try:
        data = request.get_json()
        state = data.get('state', 'OFF')
        print(f"[SIMULATOR] Actuator {actuator_id} set to {state}")
        return jsonify({"message": f"actuator {actuator_id} set to {state}"}), 200
    except Exception as e:
        print(f"[SIMULATOR] Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/telemetry/stream/mars/telemetry/radiation')
def stream_radiation():
    def generate():
        while True:
            data = {
                "timestamp": int(time.time() * 1000),
                "radiation": round(random.uniform(0.1, 10.0), 2),
                "unit": "Sv/h"
            }
            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(5)
    return app.response_class(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)