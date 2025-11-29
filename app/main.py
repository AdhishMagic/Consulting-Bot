from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from .database import engine, Base, get_db
from . import models, bookings, auth, otp_client, gmail_client
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Consulting Bot API", version="1.0.0")

# Include Routers
app.include_router(bookings.router)

# Auth Endpoints
@app.get("/auth/init", tags=["Auth"])
def auth_init():
    flow = auth.get_google_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    return RedirectResponse(authorization_url)

@app.get("/auth/callback", tags=["Auth"])
def auth_callback(request: Request, db: Session = Depends(get_db)):
    code = request.query_params.get('code')
    flow = auth.get_google_flow()
    flow.fetch_token(code=code)
    creds = flow.credentials
    auth.save_credentials(db, creds)
    return {"message": "Authentication successful. You can close this window."}

# OTP Endpoints
class OTPSendRequest(BaseModel):
    phone_number: str

class OTPVerifyRequest(BaseModel):
    request_id: str
    code: str

@app.post("/otp/send", tags=["OTP"])
def send_otp_endpoint(request: OTPSendRequest):
    return otp_client.send_otp(request.phone_number)

@app.post("/otp/verify", tags=["OTP"])
def verify_otp_endpoint(request: OTPVerifyRequest):
    return otp_client.verify_otp(request.request_id, request.code)

# Email Endpoints
class EmailSendRequest(BaseModel):
    to: str
    subject: str
    body: str

@app.post("/email/send-confirmation", tags=["Email"])
def send_email_endpoint(request: EmailSendRequest, db: Session = Depends(get_db)):
    return gmail_client.send_email(db, request.to, request.subject, request.body)

# Chat Endpoint
class ChatRequest(BaseModel):
    message: str

@app.post("/chat", tags=["Chat"])
def chat_endpoint(request: ChatRequest):
    from .gemini_client import chat_with_gemini
    response = chat_with_gemini(request.message)
    return {"response": response}

@app.get("/", tags=["General"])
def root():
    return {"message": "Consulting Bot Backend is running"}

@app.get("/health", tags=["General"])
def health_check(db: Session = Depends(get_db)):
    """
    Checks the health of the application and its dependencies.
    """
    status = {
        "status": "ok",
        "database": "unknown",
        "google_creds": "unknown",
        "vonage_api": "unknown",
        "gemini_api": "unknown"
    }

    # Check Database
    try:
        db.execute("SELECT 1")
        status["database"] = "connected"
    except Exception as e:
        status["database"] = f"error: {str(e)}"
        status["status"] = "degraded"

    # Check Google Credentials
    import os
    if os.path.exists("client_secret_1046460036418-md36vuhp52suaulkoc71n0geq87q036q.apps.googleusercontent.com.json"): # Check for specific file or generic logic
         status["google_creds"] = "present"
    else:
         # Fallback check for any client secret json
         import glob
         if glob.glob("client_secret*.json"):
             status["google_creds"] = "present"
         else:
             status["google_creds"] = "missing"
             status["status"] = "degraded"

    # Check Vonage
    if os.getenv("VONAGE_API_KEY") and os.getenv("VONAGE_API_SECRET"):
        status["vonage_api"] = "configured"
    else:
        status["vonage_api"] = "missing"
        status["status"] = "degraded"

    # Check Gemini
    if os.getenv("GEMINI_API_KEY"):
        status["gemini_api"] = "configured"
    else:
        status["gemini_api"] = "missing"
        status["status"] = "degraded"

    return status
