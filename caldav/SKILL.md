---
name: caldav
description: CalDAV client for managing calendars, events (VEVENT), and tasks (VTODO) with full recurrence support
metadata:
  {
    "openclaw": { "emoji": "📅" },
    "requires": { "pip": ["caldav", "icalendar", "python-dateutil"] },
  }
---

# CalDAV Skill

Manage CalDAV calendars, events, and todos from multiple providers (Synology, iCloud, Google, Fastmail, Nextcloud).

## Setup

### 1. Install Dependencies

```bash
pip install caldav icalendar python-dateutil
```

### 2. Configure Account

Create `~/.config/openclaw/caldav.json`:

```json
{
  "accounts": {
    "synology": {
      "url": "https://calendar.lucamanca.synology.me",
      "username": "luca",
      "password": "your_password"
    },
    "icloud": {
      "url": "https://caldav.icloud.com",
      "username": "your_email",
      "password": "app_specific_password"
    }
  }
}
```

### 3. Test Connection

```bash
python3 -c "
from scripts.caldav_client import get_client
c = get_client('synology')
print(c.get_calendars())
"
```

---

## Tool Reference

### Calendar Operations

#### list_calendars

List all available calendars.

```python
list_calendars(account: str = "synology") -> list[dict]
```

Returns:
```json
[
  {"name": "Calendar", "url": "...", "id": "..."},
  {"name": "Work", "url": "...", "id": "..."}
]
```

---

### VEVENT Operations

#### list_events

List events in a date range.

```python
list_events(
    account: str = "synology",
    calendar: str = None,
    start: str = None,  # ISO 8601
    end: str = None
) -> list[dict]
```

Example:
```python
list_events("synology", start="2026-04-07", end="2026-04-14")
```

#### get_event

Get single event by UID.

```python
get_event(account: str, uid: str, calendar: str = None) -> dict
```

#### create_event

Create new event.

```python
create_event(
    account: str = "synology",
    calendar: str = None,
    summary: str,
    dtstart: str,  # ISO 8601
    dtend: str = None,
    duration: str = None,  # e.g., "P1H"
    location: str = None,
    description: str = None,
    rrule: str = None,  # e.g., "FREQ=WEEKLY;BYDAY=MO"
    status: str = "CONFIRMED",  # CONFIRMED, TENTATIVE, CANCELLED
    attendee: list[str] = None
) -> dict
```

Example:
```python
# Weekly meeting every Monday
create_event(
    account="synology",
    summary="Team Standup",
    dtstart="2026-04-07T09:00:00",
    dtend="2026-04-07T09:30:00",
    rrule="FREQ=WEEKLY;BYDAY=MO",
    location="Office"
)
```

#### update_event

Update event fields.

```python
update_event(account: str, uid: str, calendar: str = None, **kwargs) -> dict
```

#### delete_event

Delete event.

```python
delete_event(account: str, uid: str, calendar: str = None) -> bool
```

#### get_event_status

Get event status.

```python
get_event_status(account: str, uid: str, calendar: str = None) -> str
# Returns: CONFIRMED | TENTATIVE | CANCELLED
```

---

### VTODO Operations

#### list_todos

List todos with optional filters.

```python
list_todos(
    account: str = "synology",
    todo_list: str = None,
    status: str = None,  # NEEDS-ACTION, IN-PROCESS, COMPLETED, CANCELLED
    filter_since: str = None
) -> list[dict]
```

#### get_todo

Get single todo by UID.

```python
get_todo(account: str, uid: str, todo_list: str = None) -> dict
```

#### create_todo

Create new todo.

```python
create_todo(
    account: str = "synology",
    todo_list: str = None,
    summary: str,
    dtstart: str = None,
    due: str = None,
    duration: str = None,
    priority: int = None,  # 1-9 (1 is highest)
    rrule: str = None,
    description: str = None
) -> dict
```

Example:
```python
create_todo(
    account="synology",
    summary="Review PR",
    due="2026-04-10T17:00:00",
    priority=3
)
```

#### update_todo

Update todo fields.

```python
update_todo(account: str, uid: str, todo_list: str = None, **kwargs) -> dict
```

#### delete_todo

Delete todo.

```python
delete_todo(account: str, uid: str, todo_list: str = None) -> bool
```

#### get_todo_status

Get todo status.

```python
get_todo_status(account: str, uid: str, todo_list: str = None) -> str
# Returns: NEEDS-ACTION | IN-PROCESS | COMPLETED | CANCELLED
```

#### complete_todo

Mark todo as completed.

```python
complete_todo(account: str, uid: str, todo_list: str = None) -> dict
```

#### set_todo_priority

Set todo priority.

```python
set_todo_priority(
    account: str,
    uid: str,
    priority: int,  # 1-9 (1 is highest)
    todo_list: str = None
) -> dict
```

---

### Recurrence (RRULE)

#### parse_rrule

Parse RRULE string.

```python
parse_rrule(rrule_str: str) -> dict
# Returns: {"freq": "WEEKLY", "byday": "MO", "until": "..."}
```

#### get_recurrence_dates

Calculate future dates from RRULE.

```python
get_recurrence_dates(
    rrule_str: str,
    start_date: str,
    end: str = None,
    count: int = None
) -> list[str]
```

Example:
```python
get_recurrence_dates(
    "FREQ=WEEKLY;BYDAY=MO",
    "2026-04-07",
    count=10
)
# Returns: ["2026-04-07", "2026-04-14", "2026-04-21", ...]
```

#### generate_rrule

Generate RRULE string.

```python
generate_rrule(
    freq: str,  # DAILY, WEEKLY, MONTHLY, YEARLY
    until: str = None,
    count: int = None,
    interval: int = 1,
    byday: str = None,
    bymonthday: int = None,
    bymonth: int = None
) -> str
```

---

## iCalendar Property Reference

### VEVENT Properties

| Property | Description | Example |
|----------|-------------|---------|
| UID | Unique identifier | abc123@calendar |
| DTSTART | Start datetime | 2026-04-07T09:00:00 |
| DTEND | End datetime | 2026-04-07T10:00:00 |
| DURATION | Duration (alternative to DTEND) | P1H |
| SUMMARY | Event title | Team Meeting |
| DESCRIPTION | Event description | ... |
| LOCATION | Location | Office |
| STATUS | CONFIRMED/TENTATIVE/CANCELLED | CONFIRMED |
| RRULE | Recurrence rule | FREQ=WEEKLY;BYDAY=MO |
| EXDATE | Excluded dates | 2026-04-14 |
| ATTENDEE | Participants | mailto:user@example.com |
| ORGANIZER | Organizer | mailto:organizer@example.com |
| VALARM | Reminder | TRIGGER:-PT15M |
| CLASS | PUBLIC/PRIVATE/CONFIDENTIAL | PUBLIC |
| TRANSP | TRANSPARENT/OPAQUE | OPAQUE |

### VTODO Properties

| Property | Description | Example |
|----------|-------------|---------|
| UID | Unique identifier | todo123@calendar |
| DTSTART | Start datetime | 2026-04-07T09:00:00 |
| DUE | Due datetime | 2026-04-10T17:00:00 |
| DURATION | Estimated duration | PT2H |
| SUMMARY | Task title | Review PR |
| DESCRIPTION | Task description | ... |
| STATUS | NEEDS-ACTION/IN-PROCESS/COMPLETED/CANCELLED | NEEDS-ACTION |
| PRIORITY | Priority 1-9 (1 is highest) | 3 |
| PERCENT-COMPLETE | Progress 0-100 | 50 |
| CATEGORIES | Tags | ["work", "urgent"] |
| RRULE | Recurrence rule | FREQ=DAILY |
| COMPLETED | Completion timestamp | 2026-04-07T15:30:00 |

---

## RRULE Examples

| RRULE | Description |
|-------|-------------|
| `FREQ=DAILY` | Every day |
| `FREQ=WEEKLY;BYDAY=MO` | Every Monday |
| `FREQ=WEEKLY;BYDAY=MO,WE,FR` | Mon, Wed, Fri |
| `FREQ=MONTHLY;BYMONTHDAY=1` | 1st of every month |
| `FREQ=YEARLY` | Once a year |
| `FREQ=WEEKLY;INTERVAL=2` | Every 2 weeks |
| `FREQ=DAILY;UNTIL=2026-12-31` | Daily until end of year |
| `FREQ=MONTHLY;COUNT=6` | 6 months |

---

## Troubleshooting

### Connection Issues

| Error | Solution |
|-------|----------|
| 401 Unauthorized | Check username/password |
| 403 Forbidden | Check calendar permissions |
| 404 Not Found | Check CalDAV URL |
| 409 Conflict | Resource already exists |

### Tips

- Use app-specific passwords for iCloud/Google
- Share calendar with integration for first-time access
- Check Synology logs for detailed errors