from googleapiclient.discovery import build
from .auth import get_credentials
from .utils import create_response
from sqlalchemy.orm import Session
from email.mime.text import MIMEText
import base64

def get_gmail_service(db: Session):
    creds = get_credentials(db)
    if not creds:
        return None
    return build('gmail', 'v1', credentials=creds)

def send_email(db: Session, to: str, subject: str, body: str):
    service = get_gmail_service(db)
    if not service:
        return create_response(success=False, error="Authentication failed")

    try:
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        message_body = {'raw': raw_message}
        sent_message = service.users().messages().send(userId='me', body=message_body).execute()
        
        return create_response(success=True, data={"message_id": sent_message['id']})
    except Exception as e:
        return create_response(success=False, error=str(e))
