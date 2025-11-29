from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import get_db
from .models import Booking
from .calendar_client import get_free_busy, create_event, update_event, delete_event
from .utils import create_response
from pydantic import BaseModel
import datetime

router = APIRouter()

class SlotRequest(BaseModel):
    time_min: str
    time_max: str

class BookingCreateRequest(BaseModel):
    user_email: str
    start_time: str
    end_time: str
    summary: str = "Consulting Session"
    description: str = ""

class BookingUpdateRequest(BaseModel):
    booking_id: int
    new_start_time: str
    new_end_time: str

class BookingCancelRequest(BaseModel):
    booking_id: int

@router.post("/slots/get", tags=["Slots"])
def get_slots(request: SlotRequest, db: Session = Depends(get_db)):
    return get_free_busy(db, request.time_min, request.time_max)

@router.post("/appointment/create", tags=["Appointments"])
def create_appointment(request: BookingCreateRequest, db: Session = Depends(get_db)):
    # Create Google Calendar Event
    cal_response = create_event(
        db, 
        summary=request.summary, 
        start_time=request.start_time, 
        end_time=request.end_time, 
        description=request.description,
        attendees=[request.user_email]
    )
    
    if not cal_response.get("success"):
        return cal_response

    # Save to DB
    event_id = cal_response["data"]["event_id"]
    new_booking = Booking(
        user_email=request.user_email,
        event_id=event_id,
        start_time=datetime.datetime.fromisoformat(request.start_time.replace('Z', '+00:00')),
        end_time=datetime.datetime.fromisoformat(request.end_time.replace('Z', '+00:00')),
        status="confirmed"
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    
    return create_response(success=True, data={"booking_id": new_booking.id, "event_id": event_id})

@router.post("/appointment/list", tags=["Appointments"])
def list_appointments(user_email: str, db: Session = Depends(get_db)):
    bookings = db.query(Booking).filter(Booking.user_email == user_email).all()
    data = []
    for b in bookings:
        data.append({
            "id": b.id,
            "event_id": b.event_id,
            "start": b.start_time.isoformat(),
            "end": b.end_time.isoformat(),
            "status": b.status
        })
    return create_response(success=True, data=data)

@router.post("/appointment/update", tags=["Appointments"])
def update_appointment(request: BookingUpdateRequest, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == request.booking_id).first()
    if not booking:
        return create_response(success=False, error="Booking not found")
    
    # Update Google Calendar
    cal_response = update_event(db, booking.event_id, request.new_start_time, request.new_end_time)
    if not cal_response.get("success"):
        return cal_response
    
    # Update DB
    booking.start_time = datetime.datetime.fromisoformat(request.new_start_time.replace('Z', '+00:00'))
    booking.end_time = datetime.datetime.fromisoformat(request.new_end_time.replace('Z', '+00:00'))
    db.commit()
    
    return create_response(success=True, data={"message": "Booking updated"})

@router.post("/appointment/cancel", tags=["Appointments"])
def cancel_appointment(request: BookingCancelRequest, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == request.booking_id).first()
    if not booking:
        return create_response(success=False, error="Booking not found")
    
    # Delete from Google Calendar
    cal_response = delete_event(db, booking.event_id)
    if not cal_response.get("success"):
        return cal_response
    
    # Update DB status
    booking.status = "cancelled"
    db.commit()
    
    return create_response(success=True, data={"message": "Booking cancelled"})
