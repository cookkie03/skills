#!/usr/bin/env python3
import os
import sys
import json
import argparse

def build_payloads(master_json_path, raw_sources_dir, payloads_dir):
    try:
        with open(master_json_path, 'r', encoding='utf-8') as f:
            master_map = json.load(f)
    except Exception as e:
        print(f"Error loading {master_json_path}: {e}", file=sys.stderr)
        sys.exit(1)
        
    os.makedirs(payloads_dir, exist_ok=True)
    topic_payloads = {}
    
    for entry in master_map:
        filepath = entry.get("file")
        start = entry.get("start_line", 1)
        end = entry.get("end_line", 1)
        topic = entry.get("topic", "misc").strip()
        granularity = entry.get("source_granularity", "").strip()
        
        if not filepath:
            continue
            
        full_path = os.path.join(raw_sources_dir, filepath)
        if not os.path.exists(full_path):
            print(f"Warning: Source file '{filepath}' listed in map but not found on disk. Skipping.")
            continue
            
        with open(full_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Lines are 1-indexed in the JSON map
        # Handle cases where LLM indexes incorrectly gracefully
        safe_start = max(1, start)
        safe_end = min(len(lines), max(safe_start, end))
        
        chunk = "".join(lines[safe_start-1:safe_end])
        source_cite = f"{filepath}"
        if granularity:
            source_cite += f" - {granularity}"
            
        if topic not in topic_payloads:
            topic_payloads[topic] = []
            
        topic_payloads[topic].append(f"> [Source: {source_cite}]\n{chunk}\n")
        
    for topic, chunks in topic_payloads.items():
        # Sanitize topic string for filename
        safe_topic = "".join(c if c.isalnum() else "_" for c in topic).lower()
        payload_file = os.path.join(payloads_dir, f"payload_{safe_topic}.md")
        
        with open(payload_file, 'w', encoding='utf-8') as f:
            f.write("\n\n---\n\n".join(chunks))
            
    print(f"✅ Generated {len(topic_payloads)} deterministic topic payloads in {payloads_dir}")

def main():
    parser = argparse.ArgumentParser(description="Deterministic Zero-Token Payload Builder")
    parser.add_argument("master_json", help="Path to the JSON created by llm_classifier.py (e.g. classified_map.json)")
    parser.add_argument("raw_sources_dir", help="Directory containing raw source files (e.g. .staging_unified/sources/)")
    parser.add_argument("payloads_dir", help="Output directory for generating the payloads (e.g. .staging_unified/payloads/)")
    
    args = parser.parse_args()
    build_payloads(args.master_json, args.raw_sources_dir, args.payloads_dir)

if __name__ == "__main__":
    main()
