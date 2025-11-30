from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from .database import engine, Base, get_db
from . import models, bookings, auth, otp_client, gmail_client, payment, voice
from sqlalchemy.orm import Session
from pydantic import BaseModel
from .utils import create_response
from .config import settings
import logging
import time

# Configure Structured Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("consulting_bot")

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Consulting Bot API", version="1.0.0")

# Global CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for SalesIQ
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"Path: {request.url.path} Method: {request.method} Status: {response.status_code} Time: {process_time:.4f}s")
    return response

# Global Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation Error: {exc}")
    # Return 200 OK even for validation errors so Deluge doesn't crash
    return JSONResponse(
        status_code=200,
        content=create_response(success=False, error="Validation Error", details={"errors": exc.errors()})
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP Exception: {exc.detail}")
    return JSONResponse(
        status_code=200,
        content=create_response(success=False, error=exc.detail)
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {exc}")
    return JSONResponse(
        status_code=200,
        content=create_response(success=False, error="Internal Server Error", details={"message": str(exc)})
    )

# Include Routers
app.include_router(bookings.router)
app.include_router(payment.router)
app.include_router(voice.router)

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
    if not code:
        return JSONResponse(
            status_code=200, 
            content=create_response(success=False, error="Missing authentication code", details={"message": "Please initiate authentication via /auth/init"})
        )
        
    flow = auth.get_google_flow()
    try:
        flow.fetch_token(code=code)
    except Exception as e:
        logger.error(f"Failed to fetch token: {e}")
        return JSONResponse(
            status_code=200,
            content=create_response(success=False, error="Authentication Failed", details={"message": str(e)})
        )
        
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
    logger.info(f"Sending OTP to {request.phone_number}")
    return otp_client.send_otp(request.phone_number)

@app.post("/otp/verify", tags=["OTP"])
def verify_otp_endpoint(request: OTPVerifyRequest):
    logger.info(f"Verifying OTP for {request.request_id}")
    return otp_client.verify_otp(request.request_id, request.code)

# Email Endpoints
class EmailSendRequest(BaseModel):
    to: str
    subject: str
    body: str

@app.post("/email/send-confirmation", tags=["Email"])
def send_email_endpoint(request: EmailSendRequest, db: Session = Depends(get_db)):
    logger.info(f"Sending email to {request.to}")
    return gmail_client.send_email(db, request.to, request.subject, request.body)

# Chat Endpoint
class ChatRequest(BaseModel):
    message: str
    user_id: str = "visitor"

@app.post("/chat", tags=["Chat"])
def chat_endpoint(request: ChatRequest):
    from .gemini_client import chat_with_gemini
    logger.info("Processing chat request")
    response = chat_with_gemini(request.message)
    logger.info(f"Gemini Response: {response} (Type: {type(response)})")
    return create_response(success=True, data={"response": str(response)})

class TriggerRequest(BaseModel):
    trigger: str = "default"
    user_id: str = "visitor"
    data: dict = {}

@app.post("/trigger", tags=["Chat"])
def trigger_endpoint(request: TriggerRequest):
    logger.info(f"Processing trigger: {request.trigger} for user {request.user_id}")
    # Logic to handle different triggers can go here
    # For now, we return a generic response or forward to Gemini
    from .gemini_client import chat_with_gemini
    
    prompt = f"System Event: {request.trigger}. User Data: {request.data}. Generate a welcome message or appropriate response."
    response = chat_with_gemini(prompt)
    
    return create_response(success=True, data={"reply": str(response)})

class ContextRequest(BaseModel):
    context_id: str = "default"
    user_id: str = "visitor"
    question: str = ""
    answer: str = ""

@app.post("/context", tags=["Chat"])
def context_endpoint(request: ContextRequest):
    logger.info(f"Processing context: {request.context_id} for user {request.user_id}")
    # Logic to handle context updates (e.g., collecting user info)
    from .gemini_client import chat_with_gemini
    
    prompt = f"Context: {request.context_id}. Question: {request.question}. User Answer: {request.answer}. Continue the conversation."
    response = chat_with_gemini(prompt)
    
    return create_response(success=True, data={"reply": str(response)})

    return create_response(success=True, data={"reply": response})

class FailureRequest(BaseModel):
    user_id: str
    error: str
    context: str = ""

@app.post("/failure", tags=["Chat"])
def failure_endpoint(request: FailureRequest):
    logger.error(f"Bot Failure for user {request.user_id}: {request.error} | Context: {request.context}")
    
    # We can return a specific fallback message or just a generic one
    return create_response(success=True, data={"reply": "I encountered an issue processing your request. A support agent has been notified."})

@app.get("/", tags=["General"])
def root():
    return {"message": "Consulting Bot Backend is running"}

@app.get("/health", tags=["General"])
def health_check(db: Session = Depends(get_db)):
    """
    Checks the health of the application and its dependencies.
    """
    status = {
        "status": "running",
        "deployment_mode": settings.DEPLOYMENT_MODE,
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

    return create_response(success=True, data=status)

# Simple verification endpoint for frontend connectivity checks
@app.get("/verify", tags=["General"])
def verify():
    return create_response(success=True, data={"message": "Backend reachable"})
