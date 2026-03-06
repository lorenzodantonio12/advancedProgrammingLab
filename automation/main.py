import crud
from models import AutomationRule
from cache import latest_sensor_state
from fastapi import FastAPI, HTTPException

app = FastAPI(title = "mars")

@app.get("/api/get-rules", response_model = list[AutomationRule])
def getRules():
    return crud.get_rules()

@app.post("/api/create-rule")
def createRule(rule: AutomationRule):
    id = crud.create_rule(rule)
    return {"message": "rule created!", "id_rule": id}

@app.delete("/api/delete-rule/{id_rule}")
def deleteRule(id_rule: int):
    crud.delete_rule(id_rule)
    return {"message": f"rule {id_rule} deleted"}

@app.get("/api/get-latest-state")
def getLatestState():
    return latest_sensor_state