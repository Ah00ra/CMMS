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

