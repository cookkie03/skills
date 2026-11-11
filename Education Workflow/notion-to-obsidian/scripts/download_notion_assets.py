#!/usr/bin/env python3
"""
download_notion_assets.py

Batch scans Markdown files for Notion proxy images and remote attachments,
downloads them locally into an 'Attachments/' directory, and updates the markdown
with native Obsidian wikilinks (![[Pasted image ...]] or [[filename]]).
"""

import sys
import os
import re
import urllib.parse
import urllib.request
import time
from datetime import datetime

IMAGE_REGEX = re.compile(r'!\[(.*?)\]\(((/image/[^)]+)|(https?://[^)]*(?:amazonaws\.com|notion\.so|notion\.site|requestProxiedImageUrl)[^)]*))\)')
ATTACHMENT_REGEX = re.compile(r'\[([^\]]+)\]\((https?://(?:prod-files-secure\.s3\.us-west-2\.amazonaws\.com|www\.notion\.so/signed/|.*\.notion\.site/signed/)[^)]+)\)')

def get_extension(url):
    try:
        parsed = urllib.parse.urlparse(url)
        # If url is a proxy url /image/http%3A%2F... check decoded path
        if '/image/' in parsed.path:
            unquoted = urllib.parse.unquote(parsed.path)
            sub_match = re.search(r'\.(png|jpe?g|gif|webp|svg)', unquoted, re.IGNORECASE)
            if sub_match:
                return sub_match.group(1).lower()
        match = re.search(r'\.(png|jpe?g|gif|webp|svg)', parsed.path, re.IGNORECASE)
        if match:
            return match.group(1).lower()
    except Exception:
        pass
    return 'png'

def download_file(url, target_path, base_domain="https://www.notion.so"):
    download_url = url
    if download_url.startswith('/'):
        download_url = urllib.parse.urljoin(base_domain, download_url)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    req = urllib.request.Request(download_url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        content = resp.read()
        with open(target_path, 'wb') as f:
            f.write(content)

def process_markdown_file(file_path, base_domain="https://spectacled-vacation-0ee.notion.site"):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Detect source domain if present in frontmatter or source block
    source_match = re.search(r'> \*\*Source\*\*:\s*\[Notion Guide\]\((https?://[^/)]+)', content)
    if source_match:
        base_domain = source_match.group(1)

    attachments_dir = os.path.join(os.path.dirname(file_path), "Attachments")
    os.makedirs(attachments_dir, exist_ok=True)

    modified = False
    now_ts = datetime.now().strftime("%Y%m%d%H%M%S")
    counter = 1

    def replace_image(match):
        nonlocal modified, counter
        alt_text = match.group(1)
        raw_url = match.group(2)
        
        # Skip local files or standard relative wikilinks
        if not (raw_url.startswith('/image/') or 'amazonaws.com' in raw_url or 'requestProxiedImageUrl' in raw_url or 'notion.site' in raw_url):
            return match.group(0)

        ext = get_extension(raw_url)
        filename = f"Pasted image {now_ts}_{counter}.{ext}"
        target_file = os.path.join(attachments_dir, filename)

        try:
            print(f"  Downloading image: {raw_url[:60]}... -> {filename}")
            download_file(raw_url, target_file, base_domain)
            modified = True
            counter += 1
            return f"![[{filename}]]"
        except Exception as e:
            print(f"  [ERROR] Failed to download {raw_url}: {e}", file=sys.stderr)
            return match.group(0)

    new_content = IMAGE_REGEX.sub(replace_image, content)

    # Process attachments
    def replace_attachment(match):
        nonlocal modified, counter
        link_text = match.group(1).strip()
        raw_url = match.group(2)

        clean_name = re.sub(r'[/\\?%*:|"<> ]', '_', link_text) or f"attachment_{now_ts}_{counter}"
        if '.' not in clean_name:
            clean_name += ".pdf"

        target_file = os.path.join(attachments_dir, clean_name)
        try:
            print(f"  Downloading attachment: {clean_name}")
            download_file(raw_url, target_file, base_domain)
            modified = True
            counter += 1
            return f"[[{clean_name}]]"
        except Exception as e:
            print(f"  [ERROR] Failed to download {raw_url}: {e}", file=sys.stderr)
            return match.group(0)

    new_content = ATTACHMENT_REGEX.sub(replace_attachment, new_content)

    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated: {file_path}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 download_notion_assets.py <directory_or_file> [base_domain]")
        sys.exit(1)

    target = sys.argv[1]
    base_domain = sys.argv[2] if len(sys.argv) > 2 else "https://spectacled-vacation-0ee.notion.site"

    if os.path.isfile(target):
        process_markdown_file(target, base_domain)
    elif os.path.isdir(target):
        for root, dirs, files in os.walk(target):
            # Skip hidden dirs or Attachments folders
            if "Attachments" in root or ".staging" in root:
                continue
            for file in sorted(files):
                if file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    print(f"Scanning: {file_path}")
                    process_markdown_file(file_path, base_domain)

if __name__ == "__main__":
    main()
