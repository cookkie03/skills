#!/usr/bin/env python3
"""
payload_assembly.py
Extracts tagged blocks from staging sources and multiplexes them into topic payloads.

Reads from: .staging_unified/sources/
Outputs to: .staging_unified/payloads/payload_<topic>.md
"""

import sys
import os
import re
import argparse
from pathlib import Path
from collections import defaultdict

def assemble_payloads(staging_sources_dir: str, payloads_dir: str):
    sources_path = Path(staging_sources_dir)
    if not sources_path.is_dir():
        print(f"Error: Staging dir '{sources_path}' not found.")
        sys.exit(1)

    payloads_path = Path(payloads_dir)
    payloads_path.mkdir(parents=True, exist_ok=True)
    
    # Store blocks by topic: topic_slug -> list of {ref, id, content}
    topics_store = defaultdict(list)

    # Regex to match the block:
    # %% BLOCK-START | id:042 | ref:slide_04 | tags: #topic-1, #topic-2 %%
    # content
    # %% BLOCK-END %%
    block_pattern = re.compile(
        r'%%\s*BLOCK-START\s*\|\s*id:\s*(.*?)\s*\|\s*ref:\s*(.*?)\s*\|\s*tags:\s*(.*?)\s*%%(.*?)%%\s*BLOCK-END\s*%%',
        re.DOTALL | re.IGNORECASE
    )

    print(f"🔍 Scanning files in {sources_path}...")
    file_count = 0
    block_count = 0
    
    for filepath in sources_path.rglob("*.md"):
        file_count += 1
        content = filepath.read_text(encoding="utf-8")
        
        for match in block_pattern.finditer(content):
            block_id = match.group(1).strip()
            ref = match.group(2).strip()
            tags_raw = match.group(3).strip()
            block_body = match.group(4).strip()
            
            # extract clean tags
            tags = [t.strip().replace("#", "").lower() for t in tags_raw.split(",")]
            
            for tag in tags:
                if not tag:
                    continue
                topics_store[tag].append({
                    "id": block_id,
                    "ref": ref,
                    "content": block_body
                })
            block_count += 1

    print(f"✅ Found {block_count} blocks across {file_count} staged files.")
    
    if block_count == 0:
        print("⚠️ No tags found. Check if the Tagging Sub-Agent was run.")
        return

    # Write payloads
    print(f"📦 Assembling zero-token payloads into {payloads_path}...")
    for topic, blocks in topics_store.items():
        payload_file = payloads_path / f"payload_{topic}.md"
        
        with payload_file.open("w", encoding="utf-8") as f:
            f.write(f"# Payload: {topic.upper()}\n\n")
            f.write("> **CRITICAL DIRECTIVE**: You are a Topic-Specialized Sub-Agent. Perform a Lossless Reorganization. Do not drop details, summarize out nuances, or skip bullet points. Preverve all visual placeholders (`![[...]`).\\n\\n")
            
            for b in blocks:
                f.write(f"### [Source: {b['ref']}] (ID: {b['id']})\n\n")
                f.write(b["content"] + "\n\n")
                f.write("---\n\n")
                
        print(f"   -> Created payload_{topic}.md with {len(blocks)} blocks.")
        
    print("🚀 Assembly complete! Ready for dispatch.")

def main():
    parser = argparse.ArgumentParser(description="Assemble zero-token payloads from tagged staging sources.")
    parser.add_argument("--sources", "-s", default=".staging_unified/sources", help="Directory containing tagged sources.")
    parser.add_argument("--out", "-o", default=".staging_unified/payloads", help="Directory to output assembled payloads.")
    
    args = parser.parse_args()
    assemble_payloads(args.sources, args.out)

if __name__ == "__main__":
    main()
