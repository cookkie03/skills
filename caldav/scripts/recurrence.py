"""RRULE and Recurrence Management"""
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY, YEARLY
from dateutil.parser import parse as parse_date
from datetime import datetime, timedelta
from typing import Optional

def parse_rrule(rrule_str: str) -> dict:
    """Parse RRULE string into components.
    
    Args:
        rrule_str: RRULE string (e.g., "FREQ=WEEKLY;BYDAY=MO;UNTIL=20261231")
    
    Returns:
        Dict with parsed components
    """
    result = {}
    parts = rrule_str.split(";")
    
    for part in parts:
        if "=" in part:
            key, value = part.split("=", 1)
            result[key.lower()] = value
    
    return result

def get_recurrence_dates(
    rrule_str: str,
    start_date: str,
    end: Optional[str] = None,
    count: Optional[int] = None
) -> list[str]:
    """Calculate recurrence dates from RRULE.
    
    Args:
        rrule_str: RRULE string
        start_date: Start date ISO 8601
        end: End date for calculation (optional)
        count: Maximum number of occurrences (optional)
    
    Returns:
        List of datetime strings
    """
    # Parse start
    dt_start = parse_date(start_date)
    
    # Parse RRULE
    rrule_parsed = parse_rrule(rrule_str)
    
    # Map freq
    freq_map = {
        "DAILY": DAILY,
        "WEEKLY": WEEKLY,
        "MONTHLY": MONTHLY,
        "YEARLY": YEARLY
    }
    freq = freq_map.get(rrule_parsed.get("freq", "DAILY"), DAILY)
    
    # Build kwargs
    kwargs = {"freq": freq, "dtstart": dt_start}
    
    if count:
        kwargs["count"] = count
    elif end:
        kwargs["until"] = parse_date(end)
    
    # Optional params
    if "interval" in rrule_parsed:
        kwargs["interval"] = int(rrule_parsed["interval"])
    if "byday" in rrule_parsed:
        kwargs["byweekday"] = rrule_parsed["byday"]
    if "bymonthday" in rrule_parsed:
        kwargs["bymonthday"] = int(rrule_parsed["bymonthday"])
    if "bymonth" in rrule_parsed:
        kwargs["bymonth"] = int(rrule_parsed["bymonth"])
    if "wkst" in rrule_parsed:
        kwargs["wkst"] = rrule_parsed["wkst"]
    if "setser" in rrule_parsed:
        kwargs["setser"] = rrule_parsed["setser"]
    
    # Generate dates
    try:
        dates = rrule(**kwargs)
        return [d.isoformat() for d in dates]
    except Exception as e:
        return []

def parse_exdate(exdate_str: str) -> list[datetime]:
    """Parse EXDATE string into datetime list.
    
    Args:
        exdate_str: EXDATE value (can be comma-separated)
    
    Returns:
        List of datetime objects
    """
    dates = []
    for part in exdate_str.split(","):
        try:
            dates.append(parse_date(part.strip()))
        except:
            continue
    return dates

def parse_rdate(rdate_str: str) -> list[datetime]:
    """Parse RDATE string into datetime list.
    
    Args:
        rdate_str: RDATE value (can be comma-separated)
    
    Returns:
        List of datetime objects
    """
    return parse_exdate(rdate_str)

def generate_rrule(
    freq: str,
    until: Optional[str] = None,
    count: Optional[int] = None,
    interval: int = 1,
    byday: Optional[str] = None,
    bymonthday: Optional[int] = None,
    bymonth: Optional[int] = None
) -> str:
    """Generate RRULE string.
    
    Args:
        freq: DAILY, WEEKLY, MONTHLY, or YEARLY
        until: End date ISO 8601
        count: Number of occurrences
        interval: Interval (every N periods)
        byday: Day(s) of week (MO, TU, WE, etc.)
        bymonthday: Day of month (1-31)
        bymonth: Month (1-12)
    
    Returns:
        RRULE string
    """
    parts = [f"FREQ={freq}"]
    
    if until:
        parts.append(f"UNTIL={until}")
    if count:
        parts.append(f"COUNT={count}")
    if interval > 1:
        parts.append(f"INTERVAL={interval}")
    if byday:
        parts.append(f"BYDAY={byday}")
    if bymonthday:
        parts.append(f"BYMONTHDAY={bymonthday}")
    if bymonth:
        parts.append(f"BYMONTH={bymonth}")
    
    return ";".join(parts)

def get_occurrences_in_range(
    event_data: dict,
    start: str,
    end: str
) -> list[dict]:
    """Get all occurrences of a recurring event in a date range.
    
    Args:
        event_data: Event data with rrule and dtstart
        start: Start of range
        end: End of range
    
    Returns:
        List of occurrence dicts
    """
    if not event_data.get("rrule"):
        # Single event
        dtstart = event_data.get("dtstart")
        if dtstart:
            dt = parse_date(dtstart)
            if parse_date(start) <= dt <= parse_date(end):
                return [{"date": dt.isoformat(), "instance": event_data}]
        return []
    
    # Recurring event
    rrule_str = event_data["rrule"]
    dtstart = event_data.get("dtstart")
    
    if not dtstart:
        return []
    
    dates = get_recurrence_dates(rrule_str, dtstart, end=end)
    
    occurrences = []
    for d in dates:
        dt = parse_date(d)
        if parse_date(start) <= dt <= parse_date(end):
            occurrences.append({
                "date": d,
                "instance": event_data
            })
    
    # Exclude EXDATE
    exdates = event_data.get("exdate", [])
    for ex in exdates:
        ex_dt = parse_date(ex)
        occurrences = [o for o in occurrences if parse_date(o["date"]) != ex_dt]
    
    return occurrences