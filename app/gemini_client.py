import os
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool
from . import bookings, otp_client, gmail_client
from .database import SessionLocal
import datetime

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Define Tools
def check_availability(time_min: str, time_max: str):
    """Checks calendar availability for a given time range."""
    db = SessionLocal()
    try:
        # Assuming bookings.get_free_busy is accessible or we use calendar_client directly
        from .calendar_client import get_free_busy
        return get_free_busy(db, time_min, time_max)
    finally:
        db.close()

def book_appointment(user_email: str, start_time: str, end_time: str, summary: str):
    """Books an appointment for the user."""
    db = SessionLocal()
    try:
        # We need to call the logic from bookings.create_appointment but it expects a request object.
        # It's better to call the underlying logic or construct the request.
        # For simplicity, let's call the calendar_client directly and save to DB, 
        # mimicking bookings.create_appointment logic to avoid Pydantic dependency here if possible,
        # or just reuse the router function if we can mock the dependency.
        # Actually, let's just use the client functions to keep it clean.
        from .calendar_client import create_event
        from .models import Booking
        
        cal_response = create_event(db, summary, start_time, end_time, attendees=[user_email])
        if not cal_response.get("success"):
            return cal_response

        event_id = cal_response["data"]["event_id"]
        new_booking = Booking(
            user_email=user_email,
            event_id=event_id,
            start_time=datetime.datetime.fromisoformat(start_time.replace('Z', '+00:00')),
            end_time=datetime.datetime.fromisoformat(end_time.replace('Z', '+00:00')),
            status="confirmed"
        )
        db.add(new_booking)
        db.commit()
        return {"success": True, "booking_id": new_booking.id, "event_id": event_id}
    finally:
        db.close()

def send_otp(phone_number: str):
    """Sends an OTP to the specified phone number."""
    return otp_client.send_otp(phone_number)

def verify_otp(request_id: str, code: str):
    """Verifies the OTP code."""
    return otp_client.verify_otp(request_id, code)

def send_email(to: str, subject: str, body: str):
    """Sends an email to the specified recipient."""
    db = SessionLocal()
    try:
        return gmail_client.send_email(db, to, subject, body)
    finally:
        db.close()

tools_list = [
    check_availability,
    book_appointment,
    send_otp,
    verify_otp,
    send_email
]

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    tools=tools_list
)

chat = model.start_chat(enable_automatic_function_calling=True)

def chat_with_gemini(message: str):
    try:
        response = chat.send_message(message)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"
