from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from src.models import Booking, Resource, User, Schedule
from src.users import get_current_user
from src.database import get_db


booking_router = APIRouter(
    prefix="/bookings",
    tags=["bookings"]
)


class BookingCreate(BaseModel):
    resource_id: int
    start_time: datetime
    end_time: datetime

@booking_router.post("/", status_code=status.HTTP_201_CREATED)
def create_booking(booking: BookingCreate, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    db_resource = db.query(Resource).filter(Resource.id == booking.resource_id).first()
    if not db_resource:
        raise HTTPException(status_code=404, detail="Resource not found")


    overlapping_booking = db.query(Booking).filter(
        Booking.resource_id == booking.resource_id,
        Booking.end_time > booking.start_time,
        Booking.start_time < booking.end_time
    ).first()

    if overlapping_booking:
        raise HTTPException(status_code=400, detail="Resource is already booked for this time")

    new_booking = Booking(
        user_id=current_user.id,
        resource_id=booking.resource_id,
        start_time=booking.start_time,
        end_time=booking.end_time,
        is_confirmed=True
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)


    new_schedule = Schedule(
        resource_id=booking.resource_id,
        start_time=booking.start_time,
        end_time=booking.end_time,
        is_blocked=True
    )
    db.add(new_schedule)
    db.commit()

    return new_booking

@booking_router.get("/", response_model=list[BookingCreate])
def get_all_bookings(db: Session = Depends(get_db)):
    bookings = db.query(Booking).all()
    return bookings

@booking_router.get("/my", response_model=list[BookingCreate])
def get_my_bookings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    bookings = db.query(Booking).filter(Booking.user_id == current_user.id).all()
    return bookings

@booking_router.delete("/{booking_id}")
def cancel_booking(booking_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this booking")

    db.delete(booking)


    schedule_entry = db.query(Schedule).filter(
        Schedule.resource_id == booking.resource_id,
        Schedule.start_time == booking.start_time,
        Schedule.end_time == booking.end_time,
        Schedule.is_blocked == True
    ).first()

    if schedule_entry:
        db.delete(schedule_entry)

    db.commit()
    return {"detail": "Booking cancelled successfully"}
