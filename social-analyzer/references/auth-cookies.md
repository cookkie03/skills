# Authentication via cookies

Both Instagram and TikTok rate-limit or block anonymous scraping for many
URLs (private accounts, age-gated content, or simply aggressive bot
detection). The supported, legitimate way to access content you are
authorized to see is to pass **your own logged-in session cookies** to
yt-dlp / gallery-dl. This is standard, documented behavior of both tools —
not a bypass of platform security, just reusing your own browser session.

## Option A — Cookies file (recommended, most reliable)

1. Log into instagram.com / tiktok.com in your browser.
2. Export cookies with a browser extension such as "Get cookies.txt LOCALLY"
   (Chrome/Firefox), saving Netscape-format `cookies.txt`.
3. Pass the file to any script in this skill:
   ```bash
   python scripts/analyze.py "<url>" --cookies /path/to/cookies.txt
   ```

## Option B — Read cookies directly from an installed browser

yt-dlp and gallery-dl can read cookies straight from a browser's cookie
store on the same machine:

```bash
python scripts/analyze.py "<url>" --cookies-from-browser chrome
# also supported: firefox, edge, brave, vivaldi, opera, safari
```

This avoids exporting a file but requires the browser to be installed
locally and not currently locking its cookie database.

## Notes

- Cookies expire — if you start getting `403`/login-wall errors, re-export
  them after logging in again.
- Never commit a cookies file to a repository; it is equivalent to a
  session token for your account.
- Only use this against your own account/content or content you are
  otherwise authorized to access. This skill does not implement IP
  rotation, CAPTCHA solving, or other anti-detection techniques — those
  are out of scope.
