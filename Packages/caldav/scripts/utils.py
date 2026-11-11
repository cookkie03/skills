"""Utility functions for CalDAV skill"""
from datetime import datetime
from typing import Optional

def format_datetime(dt: str, format: str = "%Y-%m-%d %H:%M") -> str:
    """Format datetime string for display."""
    try:
        d = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        return d.strftime(format)
    except:
        return dt

def parse_ical_date(value) -> Optional[datetime]:
    """Parse iCalendar date value."""
    if hasattr(value, 'dt'):
        return value.dt
    return value

def sanitize_uid(uid: str) -> str:
    """Sanitize UID for safe use."""
    return uid.strip().replace("\n", "")

def event_to_summary(event: dict) -> str:
    """Create a one-line summary of an event."""
    parts = []
    if event.get("summary"):
        parts.append(event["summary"])
    if event.get("dtstart"):
        parts.append(f"@ {format_datetime(event['dtstart'], '%d/%m %H:%M')}")
    if event.get("location"):
        parts.append(f"📍 {event['location']}")
    return " | ".join(parts) if parts else "Event"

def todo_to_summary(todo: dict) -> str:
    """Create a one-line summary of a todo."""
    parts = []
    if todo.get("summary"):
        parts.append(todo["summary"])
    if todo.get("due"):
        parts.append(f"📅 {format_datetime(todo['due'], '%d/%m')}")
    if todo.get("priority") and todo["priority"] < 5:
        parts.append(f"⚡ P{todo['priority']}")
    status_icon = {
        "NEEDS-ACTION": "⭕",
        "IN-PROCESS": "🔄",
        "COMPLETED": "✅",
        "CANCELLED": "❌"
    }
    if todo.get("status"):
        parts.append(status_icon.get(todo["status"], ""))
    return " | ".join(parts) if parts else "Task"

def filter_events_by_status(events: list[dict], status: str) -> list[dict]:
    """Filter events by status."""
    return [e for e in events if e.get("status") == status]

def filter_todos_by_status(todos: list[dict], status: str) -> list[dict]:
    """Filter todos by status."""
    return [t for t in todos if t.get("status") == status]

def group_events_by_date(events: list[dict]) -> dict[str, list[dict]]:
    """Group events by date."""
    grouped = {}
    for e in events:
        if e.get("dtstart"):
            date = e["dtstart"][:10]
            if date not in grouped:
                grouped[date] = []
            grouped[date].append(e)
    return grouped

def group_todos_by_status(todos: list[dict]) -> dict[str, list[dict]]:
    """Group todos by status."""
    grouped = {}
    for t in todos:
        status = t.get("status", "NEEDS-ACTION")
        if status not in grouped:
            grouped[status] = []
        grouped[status].append(t)
    return grouped