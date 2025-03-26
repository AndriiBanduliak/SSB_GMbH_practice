from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
import json

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    pnl_data = [
        {"date": "Jan", "value": 1000},
        {"date": "Feb", "value": 1200},
        {"date": "Mar", "value": 900},
        {"date": "Apr", "value": 1500},
        {"date": "May", "value": 2000},
        {"date": "Jun", "value": 1800},
        {"date": "Jul", "value": 2200},
        {"date": "Aug", "value": 2600},
        {"date": "Sep", "value": 2400},
        {"date": "Oct", "value": 2800},
        {"date": "Nov", "value": 3500},
        {"date": "Dec", "value": 3800},
    ]
    trades = db.query(models.Trade).limit(5).all()
    return request.app.state.templates.get_template("dashboard.html").render({
        "request": request,
        "pnl_json": json.dumps(pnl_data),
        "trades": trades
    })
