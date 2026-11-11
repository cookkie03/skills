"""VTODO Tools for CalDAV"""
from icalendar import Todo
from datetime import datetime
from typing import Optional
from .caldav_client import get_client
import uuid

def _extract_value(val):
    """Extract value from icalendar types."""
    if val is None:
        return None
    if hasattr(val, 'dt'):
        return val.dt
    return val

def _format_value(val):
    """Format value for storage."""
    if val is None:
        return None
    if isinstance(val, datetime):
        return val.isoformat()
    if hasattr(val, 'dt'):
        return str(val)
    return str(val)

def list_todos(
    account: str = "synology",
    todo_list: str = None,
    status: str = None,
    filter_since: str = None
) -> list[dict]:
    """List todos with optional filters."""
    client = get_client(account)
    
    # Get calendar
    if todo_list:
        cal = client.get_calendar(todo_list)
    else:
        calendars = client.get_calendars()
        cal = calendars[0] if calendars else None
    
    if not cal:
        return []
    
    # Fetch todos
    todos = cal.get_todos()
    
    result = []
    for t in todos:
        comp = t.icalendar_component
        if not comp:
            continue
        
        # Parse status
        status_val = str(comp.get("status", "NEEDS-ACTION"))
        if "COMPLETED" in status_val:
            todo_status = "COMPLETED"
        elif "IN-PROCESS" in status_val:
            todo_status = "IN-PROCESS"
        elif "CANCELLED" in status_val:
            todo_status = "CANCELLED"
        else:
            todo_status = "NEEDS-ACTION"
        
        if status and status != todo_status:
            continue
        
        result.append({
            "uid": _format_value(comp.get("uid")),
            "summary": _format_value(comp.get("summary")),
            "dtstart": _format_value(comp.get("dtstart")),
            "due": _format_value(comp.get("due")),
            "duration": _format_value(comp.get("duration")),
            "description": _format_value(comp.get("description")),
            "status": todo_status,
            "priority": int(comp.get("priority", 0)),
            "percent_complete": int(comp.get("percent-complete", 0)),
            "categories": [str(c) for c in comp.get("categories", [])],
            "rrule": _format_value(comp.get("rrule")),
            "completed": _format_value(comp.get("completed"))
        })
    
    return result

def get_todo(
    account: str = "synology",
    uid: str = None,
    todo_list: str = None
) -> dict:
    """Get a single todo by UID."""
    client = get_client(account)
    
    if todo_list:
        cal = client.get_calendar(todo_list)
    else:
        calendars = client.get_calendars()
        cal = calendars[0] if calendars else None
    
    if not cal:
        return None
    
    # Search for todo
    todos = cal.get_todos()
    for t in todos:
        comp = t.icalendar_component
        if not comp:
            continue
        
        uid_val = _extract_value(comp.get("uid"))
        if uid_val and str(uid_val) == uid:
            status_val = str(comp.get("status", "NEEDS-ACTION"))
            if "COMPLETED" in status_val:
                todo_status = "COMPLETED"
            elif "IN-PROCESS" in status_val:
                todo_status = "IN-PROCESS"
            elif "CANCELLED" in status_val:
                todo_status = "CANCELLED"
            else:
                todo_status = "NEEDS-ACTION"
            
            return {
                "uid": _format_value(comp.get("uid")),
                "summary": _format_value(comp.get("summary")),
                "dtstart": _format_value(comp.get("dtstart")),
                "due": _format_value(comp.get("due")),
                "duration": _format_value(comp.get("duration")),
                "description": _format_value(comp.get("description")),
                "status": todo_status,
                "priority": int(comp.get("priority", 0)),
                "percent_complete": int(comp.get("percent-complete", 0)),
                "categories": [str(c) for c in comp.get("categories", [])],
                "rrule": _format_value(comp.get("rrule")),
                "exdate": [str(ex) for ex in comp.get("exdate", [])],
                "completed": _format_value(comp.get("completed")),
                "organizer": _format_value(comp.get("organizer")),
                "attendee": [str(a) for a in comp.get("attendee", [])]
            }
    
    return None

def create_todo(
    account: str = "synology",
    todo_list: str = None,
    summary: str = None,
    dtstart: str = None,
    due: str = None,
    duration: str = None,
    priority: int = None,
    rrule: str = None,
    description: str = None
) -> dict:
    """Create a new todo."""
    client = get_client(account)
    
    # Get calendar
    if todo_list:
        cal = client.get_calendar(todo_list)
    else:
        calendars = client.get_calendars()
        cal = calendars[0] if calendars else None
    
    if not cal:
        raise ValueError("No calendar found")
    
    # Parse dates
    start_dt = None
    if dtstart:
        try:
            start_dt = datetime.fromisoformat(dtstart.replace("Z", "+00:00"))
        except:
            if hasattr(dtstart, 'dt'):
                start_dt = dtstart.dt
    
    due_dt = None
    if due:
        try:
            due_dt = datetime.fromisoformat(due.replace("Z", "+00:00"))
        except:
            if hasattr(due, 'dt'):
                due_dt = due.dt
    
    # Create todo
    todo = Todo()
    todo.add("uid", str(uuid.uuid4()))
    todo.add("summary", summary or "New Task")
    todo.add("status", "NEEDS-ACTION")
    if start_dt:
        todo.add("dtstart", start_dt)
    if due_dt:
        todo.add("due", due_dt)
    if duration:
        todo.add("duration", duration)
    if priority is not None:
        todo.add("priority", priority)
    if rrule:
        todo.add("rrule", rrule)
    if description:
        todo.add("description", description)
    
    # Save
    cal.add_todo(todo)
    
    return {"uid": str(todo["uid"]), "status": "created"}

def update_todo(
    account: str = "synology",
    uid: str = None,
    todo_list: str = None,
    keep_uid: bool = True,
    **kwargs
) -> dict:
    """Update a todo (delete and recreate)."""
    # Get existing todo
    todo_data = get_todo(account, uid, todo_list)
    if not todo_data:
        raise ValueError(f"Todo {uid} not found")
    
    # Delete old todo
    delete_todo(account, uid, todo_list)
    
    # Use same UID if keep_uid=True
    new_uid = uid if keep_uid else str(uuid.uuid4())
    
    # Build new todo with updated fields
    return _create_todo_with_uid(
        account=account,
        todo_list=todo_list,
        uid=new_uid,
        summary=kwargs.get("summary", todo_data.get("summary")),
        dtstart=kwargs.get("dtstart", todo_data.get("dtstart")),
        due=kwargs.get("due", todo_data.get("due")),
        duration=kwargs.get("duration", todo_data.get("duration")),
        priority=kwargs.get("priority", todo_data.get("priority")),
        rrule=kwargs.get("rrule", todo_data.get("rrule")),
        description=kwargs.get("description", todo_data.get("description")),
        status=kwargs.get("status")
    )

def _create_todo_with_uid(
    account: str,
    todo_list: str,
    uid: str,
    summary: str = None,
    dtstart: str = None,
    due: str = None,
    duration: str = None,
    priority: int = None,
    rrule: str = None,
    description: str = None,
    status: str = "NEEDS-ACTION"
) -> dict:
    """Create todo with specific UID."""
    client = get_client(account)
    
    if todo_list:
        cal = client.get_calendar(todo_list)
    else:
        calendars = client.get_calendars()
        cal = calendars[0] if calendars else None
    
    if not cal:
        raise ValueError("No calendar found")
    
    # Parse dates
    start_dt = None
    if dtstart:
        try:
            start_dt = datetime.fromisoformat(dtstart.replace("Z", "+00:00"))
        except:
            if hasattr(dtstart, 'dt'):
                start_dt = dtstart.dt
    
    due_dt = None
    if due:
        try:
            due_dt = datetime.fromisoformat(due.replace("Z", "+00:00"))
        except:
            if hasattr(due, 'dt'):
                due_dt = due.dt
    
    todo = Todo()
    todo.add("uid", uid)
    todo.add("summary", summary or "New Task")
    todo.add("status", status)
    if start_dt:
        todo.add("dtstart", start_dt)
    if due_dt:
        todo.add("due", due_dt)
    if duration:
        todo.add("duration", duration)
    if priority is not None:
        todo.add("priority", priority)
    if rrule:
        todo.add("rrule", rrule)
    if description:
        todo.add("description", description)
    
    cal.add_todo(todo)
    
    return {"uid": uid, "status": "updated"}

def delete_todo(
    account: str = "synology",
    uid: str = None,
    todo_list: str = None
) -> bool:
    """Delete a todo."""
    client = get_client(account)
    
    if todo_list:
        cal = client.get_calendar(todo_list)
    else:
        calendars = client.get_calendars()
        cal = calendars[0] if calendars else None
    
    if not cal:
        return False
    
    # Find and delete
    todos = cal.get_todos()
    for t in todos:
        comp = t.icalendar_component
        if not comp:
            continue
        
        uid_val = _extract_value(comp.get("uid"))
        if uid_val and str(uid_val) == uid:
            t.delete()
            return True
    
    return False

def get_todo_status(
    account: str = "synology",
    uid: str = None,
    todo_list: str = None
) -> str:
    """Get todo status."""
    todo = get_todo(account, uid, todo_list)
    if not todo:
        return None
    
    return todo.get("status", "NEEDS-ACTION")

def complete_todo(
    account: str = "synology",
    uid: str = None,
    todo_list: str = None
) -> dict:
    """Mark a todo as completed."""
    return update_todo(
        account=account,
        uid=uid,
        todo_list=todo_list,
        keep_uid=True,
        status="COMPLETED"
    )

def set_todo_priority(
    account: str = "synology",
    uid: str = None,
    priority: int = 5,
    todo_list: str = None
) -> dict:
    """Set todo priority."""
    if priority < 0 or priority > 9:
        raise ValueError("Priority must be 0-9")
    
    return update_todo(
        account=account,
        uid=uid,
        todo_list=todo_list,
        priority=priority
    )
