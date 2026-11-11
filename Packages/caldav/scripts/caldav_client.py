"""CalDAV Client Wrapper"""
import caldav
from caldav.elements import dav, cdav
from typing import Optional
from .config import get_account

class CalDAVClient:
    def __init__(self, account_name: str = "synology"):
        self.account_name = account_name
        self.client: Optional[caldav.DAVClient] = None
        self.principal: Optional[caldav.Principal] = None
    
    def connect(self) -> bool:
        """Connect to CalDAV server."""
        account = get_account(self.account_name)
        if not account:
            raise ValueError(f"Account {self.account_name} not found")
        
        base_url = account["url"].rstrip("/")
        # Synology uses /caldav.php/{username}/
        if "synology" in base_url.lower():
            url = f"{base_url}/caldav.php/{account['username']}/"
        else:
            url = base_url
        
        self.client = caldav.DAVClient(
            url=url,
            username=account["username"],
            password=account["password"]
        )
        self.principal = self.client.principal()
        return True
    
    def get_calendars(self) -> list:
        """Get all calendars (as objects)."""
        if not self.principal:
            self.connect()
        
        calendars = self.principal.calendars()
        return calendars
    
    def get_calendars_dict(self) -> list[dict]:
        """Get all calendars as dicts."""
        calendars = self.get_calendars()
        return [
            {
                "name": c.name,
                "url": str(c.url),
                "id": c.id
            }
            for c in calendars
        ]
    
    def get_calendar(self, name: str):
        """Get calendar by name."""
        if not self.principal:
            self.connect()
        
        calendars = self.principal.calendars()
        for c in calendars:
            if c.name == name:
                return c
        return None
    
    def get_todo_lists(self) -> list[dict]:
        """Get all todo lists (calendars with VTODO)."""
        if not self.principal:
            self.connect()
        
        calendars = self.principal.calendars()
        return [
            {
                "name": c.name,
                "url": c.url,
                "id": c.id
            }
            for c in calendars
        ]


def get_client(account: str = "synology") -> CalDAVClient:
    """Get a connected CalDAV client."""
    client = CalDAVClient(account)
    client.connect()
    return client