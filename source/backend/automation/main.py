import crud
import consumer
from models import AutomationRule
from cache import latest_sensor_state, latest_actuator_state
from database import create_database
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import sys
import os
from automation_engine import trigger_actuator

broker_connection = None

@asynccontextmanager
async def lifespan(app: FastAPI):

    create_database()

    global broker_connection

    print("Avvio del sistema. Connessione al broker in corso...")

    broker_connection = consumer.start_listening(host='activemq')

    yield

    print("spegnimento")

    if broker_connection:
        broker_connection.disconnect()


app = FastAPI(title = "mars", lifespan = lifespan)

@app.get("/api/get-rules", response_model = list[AutomationRule])
def getRules():
    return crud.get_rules()

@app.post("/api/create-rule")
def createRule(rule: AutomationRule):
    id = crud.create_rule(rule)

    if id is False:
        raise HTTPException(status_code = 400, detail = "Conflitto tra regole")
    
    return {"message": "rule created!", "id_rule": id}

@app.patch("/api/update-rule/{rule_id}")
def updateRule(rule_id: int, update_data: dict):
    success, message = crud.update_rule(rule_id, update_data)
    
    if success:
        return {"message": f"rule {rule_id} updated successfully!"}
    if message == "conflict":
        raise HTTPException(status_code=409, detail="Rule overlap detected")
    elif message == "not_found":
        raise HTTPException(status_code=404, detail="Rule not found")
    else:
        raise HTTPException(status_code=400, detail="Invalid data")

@app.delete("/api/delete-rule/{id_rule}")
def deleteRule(id_rule: int):
    crud.delete_rule(id_rule)
    return {"message": f"rule {id_rule} deleted"}

@app.get("/api/get-latest-state")
def getLatestState():
    return latest_sensor_state

@app.get("/api/get-actuator-state")
def getActuatorState():
    return latest_actuator_state

@app.post("/api/set-actuator")
def setActuator(actuator_id: str, state: str):
    trigger_actuator(actuator_id, state)
    latest_actuator_state[actuator_id] = state
    return {"message": f"actuator {actuator_id} set to {state}"}