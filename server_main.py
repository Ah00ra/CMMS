# server_main.py
import sqlite3
import jdatetime as jd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from db_service import DBService  # your existing class

app = FastAPI()
db = DBService("/home/ahoora/work/CMMS/god.db")


class PMDoneRequest(BaseModel):
    pm_name: str
    last_done_date: str

@app.get("/equipment/{equip_code}")
def get_equipment_detail(equip_code: int):
    data = db.get_equip_detail(equip_code)
    if data is None:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return data

@app.post("/equipment/{equip_code}/pm_done")
def mark_pm_done(equip_code: int, body: PMDoneRequest):
    try:
        equipment_pm_id = db.mark_a_pm_done(
            equipment_code=equip_code,
            pm_name=body.pm_name,
            last_done_date=body.last_done_date,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"equipment_pm_id": equipment_pm_id}

@app.get("/equipment")
def list_equipment():
    rows = db.load_equipment_table()
    return [
        {"equipment_code": code, "location": loc, "pm_type": typ}
        for (code, loc, typ) in rows
    ]

@app.delete("/equipment/{equip_code}")
def delete_equipment(equip_code: int):
    try:
        db.delete_equipment(equip_code)
        return {"status": "deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


class EquipmentCreate(BaseModel):
    equipment_code: int
    pm_type: str
    location: str

@app.post("/equipment")
def add_equipment(equip: EquipmentCreate):
    stat = db.add_new_equipment(equip.equipment_code, equip.pm_type, equip.location)
    if stat == "Duplicated":
        raise HTTPException(status_code=409, detail="Equipment code already exists")
    return {"status": "created", "equipment_code": equip.equipment_code}

@app.post("/equipment/{equip_code}/pm_tasks")
def add_pm_tasks(equip_code: int):
    db.add_pm_tasks_for_equipment(equip_code)
    return {"status": "pm_tasks_added"}