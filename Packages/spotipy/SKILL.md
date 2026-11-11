---
name: spotipy
description: Build, debug, and maintain Python integrations with Spotipy and the Spotify Web API. Use for Spotipy-specific OAuth, client setup, endpoint usage, pagination, and errors; use the Spotify Automation skill for playback control through an automation interface.
metadata:
  short-description: Develop with the Spotipy Python library
---

# Spotipy

Use [Spotipy](https://github.com/spotipy-dev/spotipy) to call Spotify Web API endpoints from Python. Treat the repository and its [official documentation](https://spotipy.readthedocs.io/en/latest/) as the source of truth for the installed version's method names and behavior; consult Spotify's current Web API documentation for endpoint availability, scopes, and restrictions.

## Choose authentication for the operation

- Use `SpotifyClientCredentials` for app-only access to endpoints that do not need user data or scopes.
- Use `SpotifyOAuth` (or the currently documented user authorization flow appropriate to the app) for user-specific data and actions. Request only the scopes the operation needs, and ensure the configured redirect URI exactly matches the Spotify developer dashboard.
- Prefer `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`, and `SPOTIPY_REDIRECT_URI` environment variables or the project's existing secret manager. Never put credentials, access tokens, refresh tokens, or token-cache contents in source control, logs, or responses. Keep client secrets on a trusted server, not browser or mobile code.
- Reuse the project's existing auth and cache configuration when present. Do not trigger a new consent flow or change a user's Spotify data as an incidental debugging step.

## Work with the API

- Inspect the installed Spotipy version and use its matching API; do not assume a method or endpoint exists just because it appears in an old example.
- Check Spotify's current endpoint documentation and required scopes before implementing a user operation. Spotify API access and endpoint rules can change independently of Spotipy.
- Handle paginated results until no `next` page remains; Spotipy's `*_all` helpers may be suitable where available. Avoid silently treating one page as a complete collection.
- Handle `SpotifyException` and HTTP failures deliberately. Respect `Retry-After` on 429 responses, use bounded retries for transient failures, and avoid retrying non-idempotent writes blindly.
- Keep API calls narrow and avoid fetching or changing more user data than the request needs. For playlist, library, or playback writes, make the intended effect clear and require user authorization before executing a real external mutation.

## Typical setup

```python
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
results = sp.search(q="artist:Radiohead", type="artist", limit=10)
```

For user access, use `SpotifyOAuth` with the minimum required scope and credentials supplied through the environment or existing project configuration. Follow the installed version's official docs for cache handler and redirect behavior.
