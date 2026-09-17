#!/usr/bin/env python3
import os
import sys
import json
import argparse
import requests
from glob import glob

def call_classifier(text_chunk, filepath, topics, endpoint, model, api_key):
    system_prompt = (
        "You are an expert NLP classifier. Analyze the provided text, which has line numbers prepended.\n"
        f"Map the content into the following topics: {topics}\n"
        "Return ONLY a strictly valid JSON array of objects. Do not wrap in markdown code blocks. "
        "Each object must have exactly these keys:\n"
        f'- "file": "{filepath}"\n'
        '- "start_line": integer (the physical starting line number according to the prefix)\n'
        '- "end_line": integer (the physical ending line number)\n'
        '- "topic": string (must be one of the provided topics, or "misc")\n'
        '- "source_granularity": string (e.g., "slide 3", "minute 2:10", "section 1.2" if detectable, otherwise "")\n'
        "Coverage must be exhaustive. Every line of the input must belong to at least one topic block. "
        "Do not leave any lines untagged."
    )

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text_chunk}
        ],
        "temperature": 0.1
    }

    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=120)
        response.raise_for_status()
        
        content = response.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        
        # Clean up Markdown JSON fences if hallucinaton occurs
        if content.startswith("```json"): content = content[7:]
        if content.startswith("```"): content = content[3:]
        if content.endswith("```"): content = content[:-3]
            
        return json.loads(content.strip())
    except Exception as e:
        print(f"Error classifying {filepath}: {e}", file=sys.stderr)
        return []

def main():
    parser = argparse.ArgumentParser(description="LLM Classifier Map Phase")
    parser.add_argument("sources_dir", help="Directory containing raw source files (.md, .txt)")
    parser.add_argument("output_json", help="Path to save the master classified_map.json")
    parser.add_argument("--topics", required=True, help="Comma-sep list of topics, or path to a text file with topics")
    parser.add_argument("--endpoint", default=os.getenv("OMNIROUTE_URL", "http://100.74.207.0/v1/chat/completions"), help="LLM API Endpoint")
    parser.add_argument("--model", default=os.getenv("OMNIROUTE_MODEL", "auto/best-free"), help="Model name")
    parser.add_argument("--api-key", default=os.getenv("OMNIROUTE_API_KEY", os.getenv("OPENAI_API_KEY", "")), help="API Key")
    parser.add_argument("--chunk-lines", type=int, default=500, help="Max lines per request to avoid context overflow")
    
    args = parser.parse_args()

    # Resolve topics
    if os.path.isfile(args.topics):
        with open(args.topics, 'r', encoding='utf-8') as f:
            topics_list = [line.strip() for line in f if line.strip()]
    else:
        topics_list = [t.strip() for t in args.topics.split(",")]

    topics_str = ", ".join(topics_list)
    master_map = []
    
    search_path = os.path.join(args.sources_dir, "**", "*.*")
    files = [f for f in glob(search_path, recursive=True) if f.endswith(('.md', '.txt'))]
    
    print(f"Found {len(files)} source files. Starting classification (Model: {args.model})...")

    for fpath in files:
        rel_path = os.path.relpath(fpath, args.sources_dir)
        print(f"Processing: {rel_path}")
        
        with open(fpath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for chunk_idx in range(0, len(lines), args.chunk_lines):
            chunk_lines = lines[chunk_idx:chunk_idx + args.chunk_lines]
            
            # Inject physical line numbers
            numbered_text = ""
            for local_i, original_line in enumerate(chunk_lines):
                physical_line = chunk_idx + local_i + 1
                numbered_text += f"{physical_line}| {original_line}"
                
            print(f"  -> Sending lines {chunk_idx+1} to {chunk_idx + len(chunk_lines)}...")
            
            chunk_mapping = call_classifier(
                text_chunk=numbered_text, 
                filepath=rel_path,
                topics=topics_str,
                endpoint=args.endpoint,
                model=args.model,
                api_key=args.api_key
            )
            
            if chunk_mapping:
                master_map.extend(chunk_mapping)

    with open(args.output_json, 'w', encoding='utf-8') as f:
        json.dump(master_map, f, indent=2, ensure_ascii=False)
        
    print(f"\n✅ Created JSON Master Map with {len(master_map)} blocks -> {args.output_json}")

if __name__ == "__main__":
    main()
