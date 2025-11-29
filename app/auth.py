import os
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from sqlalchemy.orm import Session
from .models import OAuthToken
from .database import get_db
import json
import datetime

# Scopes required for the application
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/userinfo.email',
    'openid'
]

from .config import settings

# ... (imports)

def get_google_flow(redirect_uri=None):
    """
    Creates a Google OAuth Flow instance.
    """
    client_config = {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=redirect_uri or settings.get_redirect_uri()
    )
    return flow

def get_credentials(db: Session, user_email: str = None):
    """
    Retrieves and refreshes Google Credentials.
    If user_email is provided, tries to fetch from DB.
    Otherwise uses env vars or default logic.
    """
    # For this bot, we might be using a central account for calendar/gmail
    # In a multi-user scenario, we'd fetch by user_email.
    # Here we assume a single 'admin' or 'service' account is used for the bot's calendar.
    # Or we use the token stored in env/DB for the bot's operation.
    
    # Strategy: Try to get the latest token from DB (assuming single user flow for bot owner)
    # If not in DB, check env vars for refresh token to reconstruct.
    
    token_record = db.query(OAuthToken).first() # simplistic for single-user bot
    
    creds = None
    
    if token_record:
        creds = Credentials(
            token=token_record.access_token,
            refresh_token=token_record.refresh_token,
            token_uri=token_record.token_uri,
            client_id=token_record.client_id,
            client_secret=token_record.client_secret,
            scopes=token_record.scopes.split(','),
            expiry=token_record.expiry
        )
    elif os.getenv("GOOGLE_REFRESH_TOKEN"):
        # Fallback to env var reconstruction
        creds = Credentials(
            token=None,
            refresh_token=os.getenv("GOOGLE_REFRESH_TOKEN"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv("GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
            scopes=SCOPES
        )

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        # Update DB if we have a record
        if token_record:
            token_record.access_token = creds.token
            token_record.expiry = creds.expiry
            db.commit()
            
    return creds

def save_credentials(db: Session, creds, user_email: str = "admin@example.com"):
    """
    Saves credentials to the database.
    """
    token_record = db.query(OAuthToken).filter(OAuthToken.user_email == user_email).first()
    if not token_record:
        token_record = OAuthToken(user_email=user_email)
        db.add(token_record)
    
    token_record.access_token = creds.token
    token_record.refresh_token = creds.refresh_token
    token_record.token_uri = creds.token_uri
    token_record.client_id = creds.client_id
    token_record.client_secret = creds.client_secret
    token_record.scopes = ",".join(creds.scopes)
    token_record.expiry = creds.expiry
    
    db.commit()
