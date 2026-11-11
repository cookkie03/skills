"""CalDAV Config Management"""
import json
import os
from pathlib import Path

CONFIG_PATH = Path.home() / ".config" / "openclaw" / "caldav.json"

def load_config() -> dict:
    """Load CalDAV configuration."""
    if not CONFIG_PATH.exists():
        return {"accounts": {}}
    with open(CONFIG_PATH) as f:
        return json.load(f)

def save_config(config: dict) -> None:
    """Save CalDAV configuration."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)

def get_account(name: str = "synology") -> dict | None:
    """Get account credentials."""
    config = load_config()
    return config.get("accounts", {}).get(name)

def add_account(name: str, url: str, username: str, password: str) -> None:
    """Add or update an account."""
    config = load_config()
    if "accounts" not in config:
        config["accounts"] = {}
    config["accounts"][name] = {
        "url": url,
        "username": username,
        "password": password
    }
    save_config(config)

def list_accounts() -> list[str]:
    """List all configured accounts."""
    config = load_config()
    return list(config.get("accounts", {}).keys())