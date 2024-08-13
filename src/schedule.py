from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from src.database import get_db
from src.models import Schedule, Resource, User
from src.users import get_current_user, verify_admin


schedule_router = APIRouter(
    prefix="/schedule",
    tags=["schedule"]
)

class ScheduleCreate(BaseModel):
    resource_id: int
    start_time: datetime
    end_time: datetime
    is_blocked: bool = False

@schedule_router.get("/")
def get_schedule(db: Session = Depends(get_db)):
    schedules = db.query(Schedule).all()
    return schedules

@schedule_router.post("/block", status_code=status.HTTP_201_CREATED)
def block_resource(schedule: ScheduleCreate, db: Session = Depends(get_db), current_user: User = Depends(verify_admin)):
    db_resource = db.query(Resource).filter(Resource.id == schedule.resource_id).first()
    if not db_resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    new_schedule = Schedule(
        resource_id=schedule.resource_id,
        start_time=schedule.start_time,
        end_time=schedule.end_time,
        is_blocked=True
    )
    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)
    return new_schedule
