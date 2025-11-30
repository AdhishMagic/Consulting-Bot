import os
import logging
import datetime
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool  # type: ignore
from . import bookings, otp_client, gmail_client
from .database import SessionLocal

logger = logging.getLogger("consulting_bot.gemini")

# Configure Gemini
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
    except Exception as e:
        logger.error(f"Failed to configure Gemini client: {e}")
else:
    logger.warning("GEMINI_API_KEY not set; Gemini calls will return error message.")

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

def create_payment_link(booking_id: int, amount: int, currency: str = "INR"):
    """Generates a payment link for a booking."""
    import razorpay
    from .models import Payment
    
    db = SessionLocal()
    try:
        key_id = os.getenv("RAZORPAY_KEY_ID")
        key_secret = os.getenv("RAZORPAY_KEY_SECRET")
        
        if not key_id or not key_secret:
            return {"error": "Razorpay credentials missing"}
            
        client = razorpay.Client(auth=(key_id, key_secret))
        
        data = {
            "amount": amount * 100, # subunits
            "currency": currency,
            "receipt": f"booking_{booking_id}",
            "payment_capture": 1
        }
        order = client.order.create(data=data)
        
        # Save Payment Record
        # We need a user_id, but for this tool we might not have it directly from the prompt 
        # unless passed. We'll assume a placeholder or try to fetch from booking if possible.
        # For now, let's use a default or 0 if not provided.
        # Ideally, the bot should ask for user_id or we infer it.
        # Let's pass user_id=0 for now as it's required by model but maybe not critical for link generation.
        
        new_payment = Payment(
            booking_id=booking_id,
            user_id=0, # Placeholder
            order_id=order['id'],
            amount=amount,
            currency=currency,
            status="created"
        )
        db.add(new_payment)
        db.commit()
        
        payment_link = f"https://checkout.razorpay.com/v1/checkout.js?order_id={order['id']}"
        return {"success": True, "payment_link": payment_link, "order_id": order['id']}
        
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()

tools_list = [
    check_availability,
    book_appointment,
    send_otp,
    verify_otp,
    send_email,
    create_payment_link
]

_model = None  # lazy init

PREFERRED_MODELS = [
    "gemini-1.5-flash-002",
    "gemini-1.5-pro-002",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-pro",
]

def _select_model():
    if not API_KEY:
        return None
    # Prefer direct model names first to avoid API version mismatches
    for candidate in PREFERRED_MODELS:
        try:
            model_name = candidate if candidate.startswith("models/") else f"models/{candidate}"
            mdl = genai.GenerativeModel(model_name=model_name, tools=tools_list)
            logger.info(f"Selected Gemini model: {model_name}")
            return mdl
        except Exception as e:
            logger.warning(f"Failed to init model '{candidate}': {e}")
            continue
    # As a last resort, attempt listing and pick any that supports generateContent
    try:
        available = list(genai.list_models())
        support = {m.name: m for m in available if getattr(m, "supported_generation_methods", None) and "generateContent" in m.supported_generation_methods}
        if support:
            any_name = next(iter(support.keys()))
            logger.warning(f"Preferred models unavailable. Falling back to {any_name}")
            return genai.GenerativeModel(model_name=any_name, tools=tools_list)
    except Exception as e:
        logger.error(f"Unable to list Gemini models: {e}")
    logger.error("No suitable Gemini model could be initialized.")
    return None

def chat_with_gemini(message: str):
    """Send a message to Gemini with dynamic model selection and graceful fallbacks."""
    if not API_KEY:
        # Friendly fallback response when API key is missing
        safe_msg = (message or "").strip()
        if not safe_msg:
            safe_msg = "your message"
        return (
            "Hi! I'm running in demo mode right now (no Gemini API key configured). "
            "I can still respond: You said: '" + safe_msg + "'. "
            "To enable full AI replies, set GEMINI_API_KEY in the environment."
        )
    global _model
    if _model is None:
        _model = _select_model()
        if _model is None:
            return "Error: No available Gemini model"
    try:
        chat = _model.start_chat(enable_automatic_function_calling=True)
        response = chat.send_message(message)
        return getattr(response, "text", str(response))
    except Exception as e:
        # On model not found errors, attempt one re-selection then retry once
        err_msg = str(e)
        if "not found" in err_msg or "404" in err_msg:
            logger.warning(f"Model error '{err_msg}', re-selecting model...")
            _model = _select_model()
            if _model is None:
                return f"Error: {err_msg} (and no fallback model available)"
            try:
                chat = _model.start_chat(enable_automatic_function_calling=True)
                response = chat.send_message(message)
                return getattr(response, "text", str(response))
            except Exception as e2:
                return f"Error: {str(e2)}"
        return f"Error: {err_msg}"
