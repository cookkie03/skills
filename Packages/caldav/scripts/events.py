"""VEVENT Tools for CalDAV"""
from icalendar import Event, Calendar
from datetime import datetime, timedelta
from typing import Optional
from .caldav_client import get_client
import uuid

def list_calendars(account: str = "synology") -> list:
    """List all available calendars."""
    client = get_client(account)
    calendars = client.get_calendars()
    return [{"name": c.name, "url": str(c.url), "id": c.id} for c in calendars]

def list_events(
    account: str = "synology",
    calendar: str = None,
    start: str = None,
    end: str = None
) -> list[dict]:
    """List events in a date range."""
    client = get_client(account)
    
    # Parse dates
    if start:
        dt_start = datetime.fromisoformat(start.replace("Z", "+00:00"))
    else:
        dt_start = datetime.now()
    
    if end:
        dt_end = datetime.fromisoformat(end.replace("Z", "+00:00"))
    else:
        dt_end = dt_start + timedelta(days=7)
    
    # Get calendar
    if calendar:
        cal = client.get_calendar(calendar)
    else:
        calendars = client.get_calendars()
        cal = calendars[0] if calendars else None
    
    if not cal:
        return []
    
    # Fetch events
    events = cal.get_events()
    
    result = []
    for e in events:
        try:
            comp = e.icalendar_component
            if not comp:
                continue
                
            # Get dtstart for filtering
            dtstart = comp.get("dtstart")
            if dtstart:
                dt_val = getattr(dtstart, 'dt', None)
                if dt_val and not (dt_start <= dt_val <= dt_end):
                    continue
            
            result.append({
                "uid": str(comp.get("uid", "")),
                "summary": str(comp.get("summary", "")),
                "dtstart": str(comp.get("dtstart", "")),
                "dtend": str(comp.get("dtend", "")),
                "duration": str(comp.get("duration", "")),
                "location": str(comp.get("location", "")),
                "description": str(comp.get("description", "")),
                "status": str(comp.get("status", "CONFIRMED")),
                "rrule": str(comp.get("rrule", "")),
                "attendee": [str(a) for a in comp.get("attendee", [])]
            })
        except Exception as ex:
            continue
    
    return result

def get_event(account: str = "synology", uid: str = None, calendar: str = None) -> dict:
    """Get a single event by UID."""
    client = get_client(account)
    
    if calendar:
        cal = client.get_calendar(calendar)
    else:
        calendars = client.get_calendars()
        cal = calendars[0] if calendars else None
    
    if not cal:
        return None
    
    # Search for event via get_events
    all_events = cal.get_events()
    for e in all_events:
        comp = e.icalendar_component
        if comp and str(comp.get("uid", "")) == uid:
            return {
                "uid": str(comp.get("uid", "")),
                "summary": str(comp.get("summary", "")),
                "dtstart": str(comp.get("dtstart", "")),
                "dtend": str(comp.get("dtend", "")),
                "duration": str(comp.get("duration", "")),
                "location": str(comp.get("location", "")),
                "description": str(comp.get("description", "")),
                "status": str(comp.get("status", "CONFIRMED")),
                "rrule": str(comp.get("rrule", "")),
                "exdate": [str(ex) for ex in comp.get("exdate", [])],
                "attendee": [str(a) for a in comp.get("attendee", [])],
                "organizer": str(comp.get("organizer", "")),
                "class": str(comp.get("class", "")),
                "transp": str(comp.get("transp", ""))
            }
    
    return None

def create_event(
    account: str = "synology",
    calendar: str = None,
    summary: str = None,
    dtstart: str = None,
    dtend: str = None,
    duration: str = None,
    location: str = None,
    description: str = None,
    rrule: str = None,
    status: str = "CONFIRMED",
    attendee: list[str] = None
) -> dict:
    """Create a new event."""
    client = get_client(account)
    
    # Get calendar
    if calendar:
        cal = client.get_calendar(calendar)
    else:
        calendars = client.get_calendars()
        cal = calendars[0] if calendars else None
    
    if not cal:
        raise ValueError("No calendar found")
    
    # Parse dates
    start_dt = datetime.fromisoformat(dtstart.replace("Z", "+00:00")) if dtstart else datetime.now()
    end_dt = datetime.fromisoformat(dtend.replace("Z", "+00:00")) if dtend else None
    
    # Create event
    event = Event()
    event.add("uid", str(uuid.uuid4()))
    event.add("summary", summary or "New Event")
    event.add("dtstart", start_dt)
    if end_dt:
        event.add("dtend", end_dt)
    elif duration:
        event.add("duration", duration)
    if location:
        event.add("location", location)
    if description:
        event.add("description", description)
    event.add("status", status)
    if rrule:
        event.add("rrule", rrule)
    if attendee:
        for a in attendee:
            event.add("attendee", a)
    
    # Save
    cal.add_event(event)
    
    return {"uid": str(event["uid"]), "status": "created"}

def update_event(
    account: str = "synology",
    uid: str = None,
    calendar: str = None,
    **kwargs
) -> dict:
    """Update an event."""
    event_data = get_event(account, uid, calendar)
    if not event_data:
        raise ValueError(f"Event {uid} not found")
    
    client = get_client(account)
    
    if calendar:
        cal = client.get_calendar(calendar)
    else:
        calendars = client.get_calendars()
        cal = calendars[0] if calendars else None
    
    if not cal:
        raise ValueError("No calendar found")
    
    # Delete old event
    delete_event(account, uid, calendar)
    
    # Create new with updated fields
    event_data.update(kwargs)
    return create_event(
        account=account,
        calendar=calendar,
        summary=event_data.get("summary"),
        dtstart=event_data.get("dtstart"),
        dtend=event_data.get("dtend"),
        location=event_data.get("location"),
        description=event_data.get("description"),
        status=event_data.get("status"),
        rrule=event_data.get("rrule")
    )

def delete_event(
    account: str = "synology",
    uid: str = None,
    calendar: str = None
) -> bool:
    """Delete an event."""
    client = get_client(account)
    
    if calendar:
        cal = client.get_calendar(calendar)
    else:
        calendars = client.get_calendars()
        cal = calendars[0] if calendars else None
    
    if not cal:
        return False
    
    # Find and delete
    all_events = cal.get_events()
    for e in all_events:
        comp = e.icalendar_component
        if comp and str(comp.get("uid", "")) == uid:
            e.delete()
            return True
    
    return False

def get_event_status(
    account: str = "synology",
    uid: str = None,
    calendar: str = None
) -> str:
    """Get event status."""
    event = get_event(account, uid, calendar)
    if not event:
        return None
    
    return event.get("status", "CONFIRMED")
