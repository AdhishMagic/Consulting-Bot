from googleapiclient.discovery import build
from .auth import get_credentials
from .utils import create_response
from sqlalchemy.orm import Session
import datetime
import pytz

def get_calendar_service(db: Session):
    creds = get_credentials(db)
    if not creds:
        return None
    return build('calendar', 'v3', credentials=creds)

def get_free_busy(db: Session, time_min: str, time_max: str):
    """
    Fetch free/busy information.
    """
    service = get_calendar_service(db)
    if not service:
        return create_response(success=False, error="Authentication failed")

    body = {
        "timeMin": time_min,
        "timeMax": time_max,
        "timeZone": "UTC",
        "items": [{"id": "primary"}]
    }

    try:
        events_result = service.freebusy().query(body=body).execute()
        calendars = events_result.get('calendars', {})
        primary = calendars.get('primary', {})
        busy = primary.get('busy', [])
        
        # Calculate free slots (simplified logic: 30 min slots)
        # Note: A robust implementation would take the full range and subtract busy chunks.
        # For this example, we return the busy list and let the frontend or a helper process it,
        # OR we can generate available slots here. The prompt asks for "Availability must return 30-minute slots".
        
        # Let's generate slots.
        start = datetime.datetime.fromisoformat(time_min.replace('Z', '+00:00'))
        end = datetime.datetime.fromisoformat(time_max.replace('Z', '+00:00'))
        
        slots = []
        current = start
        while current + datetime.timedelta(minutes=30) <= end:
            slot_end = current + datetime.timedelta(minutes=30)
            is_busy = False
            for b in busy:
                b_start = datetime.datetime.fromisoformat(b['start'].replace('Z', '+00:00'))
                b_end = datetime.datetime.fromisoformat(b['end'].replace('Z', '+00:00'))
                
                # Check overlap
                if max(current, b_start) < min(slot_end, b_end):
                    is_busy = True
                    break
            
            if not is_busy:
                slots.append({
                    "start": current.isoformat(),
                    "end": slot_end.isoformat()
                })
            
            current = slot_end

        return create_response(success=True, slots=slots)

    except Exception as e:
        return create_response(success=False, error=str(e))

def create_event(db: Session, summary: str, start_time: str, end_time: str, description: str = "", attendees: list = []):
    service = get_calendar_service(db)
    if not service:
        return create_response(success=False, error="Authentication failed")

    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_time,
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'UTC',
        },
        'attendees': [{'email': email} for email in attendees],
    }

    try:
        event = service.events().insert(calendarId='primary', body=event).execute()
        return create_response(success=True, data={"event_id": event.get('id'), "link": event.get('htmlLink')})
    except Exception as e:
        return create_response(success=False, error=str(e))

def update_event(db: Session, event_id: str, start_time: str, end_time: str):
    service = get_calendar_service(db)
    if not service:
        return create_response(success=False, error="Authentication failed")

    try:
        # First get the event
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
        
        event['start']['dateTime'] = start_time
        event['end']['dateTime'] = end_time
        
        updated_event = service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
        return create_response(success=True, data={"event_id": updated_event.get('id')})
    except Exception as e:
        return create_response(success=False, error=str(e))

def delete_event(db: Session, event_id: str):
    service = get_calendar_service(db)
    if not service:
        return create_response(success=False, error="Authentication failed")

    try:
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return create_response(success=True, data={"message": "Event deleted"})
    except Exception as e:
        return create_response(success=False, error=str(e))
