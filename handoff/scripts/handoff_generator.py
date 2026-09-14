#!/usr/bin/env python3
"""
Handoff Generator: Encapsulated script to format, redact, and write
structured handoff documents for cross-agent session continuity.
"""

import argparse
import datetime
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


SECRET_PATTERNS = [
    # OpenAI, Anthropic, Gemini, HuggingFace, GitHub, AWS, Generic keys
    (r"sk-[a-zA-Z0-9_-]{20,}", "[REDACTED_API_KEY]"),
    (r"gh[pousr]_[a-zA-Z0-9]{30,}", "[REDACTED_GITHUB_TOKEN]"),
    (r"glpat-[a-zA-Z0-9\-]{20,}", "[REDACTED_GITLAB_TOKEN]"),
    (r"AKIA[0-9A-Z]{16}", "[REDACTED_AWS_KEY]"),
    (r"AIza[0-9A-Za-z\-_]{35}", "[REDACTED_GOOGLE_KEY]"),
    (r"xox[baprs]-[0-9a-zA-Z]{10,48}", "[REDACTED_SLACK_TOKEN]"),
    (r"hf_[a-zA-Z0-9]{30,}", "[REDACTED_HF_TOKEN]"),
    # Bearer tokens and JWTs
    (r"Bearer\s+eyJ[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+", "Bearer [REDACTED_JWT]"),
    (r"Bearer\s+[a-zA-Z0-9\-_]{20,}", "Bearer [REDACTED_TOKEN]"),
    # Key-Value assignments
    (r'(?i)(password|secret|token|api_key|apikey|access_token|private_key)\s*[:=]\s*["\']?([^"\'\s;,]{6,})["\']?', r'\1: "[REDACTED]"'),
]


def redact_secrets(text: str) -> str:
    """Redact sensitive credentials, tokens, and keys from the text."""
    if not text:
        return ""
    redacted = text
    for pattern, replacement in SECRET_PATTERNS:
        redacted = re.sub(pattern, replacement, redacted)
    return redacted


def get_git_context(directory: Path) -> dict:
    """Extract git branch, commit hash, and dirty status if directory is in a git repository."""
    dir_path = Path(directory).resolve()
    context = {
        "is_repo": False,
        "branch": "N/A",
        "commit": "N/A",
        "dirty": False,
    }
    try:
        res_branch = subprocess.run(
            ["git", "-C", str(dir_path), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        if res_branch.returncode == 0:
            context["is_repo"] = True
            context["branch"] = res_branch.stdout.strip()

            res_commit = subprocess.run(
                ["git", "-C", str(dir_path), "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
                timeout=3,
            )
            if res_commit.returncode == 0:
                context["commit"] = res_commit.stdout.strip()

            res_status = subprocess.run(
                ["git", "-C", str(dir_path), "status", "--porcelain"],
                capture_output=True,
                text=True,
                timeout=3,
            )
            if res_status.returncode == 0:
                context["dirty"] = bool(res_status.stdout.strip())
    except Exception:
        pass
    return context


def build_handoff_document(metadata: dict, sections: dict) -> str:
    """Assemble standardized Obsidian/Markdown handoff document with YAML frontmatter."""
    title = metadata.get("title", "Handoff Document")
    date_str = metadata.get("date", datetime.date.today().isoformat())
    time_str = datetime.datetime.now().strftime("%H:%M:%S")
    goal = metadata.get("next_session_focus", "Continue ongoing task")
    cwd = metadata.get("cwd", os.getcwd())
    git_branch = metadata.get("git_branch", "N/A")
    git_commit = metadata.get("git_commit", "N/A")

    lines = []
    lines.append("---")
    lines.append('type: "Agent Handoff Document"')
    lines.append(f'date: "{date_str}"')
    lines.append(f'time: "{time_str}"')
    lines.append(f'working_directory: "{cwd}"')
    lines.append(f'next_session_focus: "{goal}"')
    if git_branch != "N/A":
        lines.append(f'git_branch: "{git_branch}"')
        lines.append(f'git_commit: "{git_commit}"')
    lines.append("tags:")
    lines.append("  - agent-handoff")
    lines.append("  - session-transition")
    lines.append("---")
    lines.append("")

    if title.startswith("Handoff Document"):
        clean_title = title
    elif title.lower().startswith("handoff:"):
        clean_title = f"Handoff Document: {title[8:].strip()}"
    elif title.lower().startswith("handoff -"):
        clean_title = f"Handoff Document: {title[9:].strip()}"
    else:
        clean_title = f"Handoff Document: {title}"
    lines.append(f"# {clean_title}")
    lines.append("")
    lines.append(f"> **Generated**: {date_str} {time_str} | **Directory**: `{cwd}`")
    if git_branch != "N/A":
        lines.append(f"> **Git**: Branch `{git_branch}` (`{git_commit}`)")
    lines.append(f"> **Next Session Focus**: {goal}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Section 1: Executive Summary & Objective
    lines.append("## 1. Executive Summary & Objective")
    summary = sections.get("summary", "Session context transition.")
    lines.append(f"{summary}")
    lines.append("")

    # Section 2: Completed Work & Changes
    lines.append("## 2. Completed Work & Changes")
    completed = sections.get("completed_work", [])
    if isinstance(completed, str):
        completed = [c.strip() for c in completed.split(";") if c.strip()]
    if completed:
        for item in completed:
            lines.append(f"- [x] {item}")
    else:
        lines.append("- No specific tasks marked completed.")
    lines.append("")

    # Section 3: Key Decisions & Rationale
    lines.append("## 3. Key Decisions & Rationale")
    decisions = sections.get("key_decisions", [])
    if isinstance(decisions, str):
        decisions = [d.strip() for d in decisions.split(";") if d.strip()]
    if decisions:
        for item in decisions:
            lines.append(f"- **Decision**: {item}")
    else:
        lines.append("- No architectural or structural decisions recorded.")
    lines.append("")

    # Section 4: Critical File Paths & Artifacts
    lines.append("## 4. Critical File Paths & Artifacts")
    files = sections.get("files_modified", [])
    if isinstance(files, str):
        files = [f.strip() for f in files.split(";") if f.strip()]
    if files:
        for item in files:
            lines.append(f"- `{item}`")
    else:
        lines.append("- No files modified or referenced.")
    lines.append("")

    # Section 5: Current State & Known Blockers
    lines.append("## 5. Current State & Known Blockers")
    blockers = sections.get("blockers", [])
    if isinstance(blockers, str):
        blockers = [b.strip() for b in blockers.split(";") if b.strip()]
    if blockers:
        for item in blockers:
            lines.append(f"- [ ] ⚠️ {item}")
    else:
        lines.append("- No active blockers or pending questions.")
    lines.append("")

    # Section 6: Actionable Next Steps
    lines.append("## 6. Actionable Next Steps for Incoming Agent")
    next_steps = sections.get("next_steps", [])
    if isinstance(next_steps, str):
        next_steps = [n.strip() for n in next_steps.split(";") if n.strip()]
    if next_steps:
        for item in next_steps:
            lines.append(f"- [ ] {item}")
    else:
        lines.append(f"- [ ] Continue with goal: {goal}")
    lines.append("")

    # Section 7: Suggested Skills for Incoming Agent
    lines.append("## 7. Suggested Skills for Incoming Agent")
    skills = sections.get("suggested_skills", [])
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(",") if s.strip()]
    if skills:
        lines.append("The incoming agent should invoke the following skills when resuming:")
        for s in skills:
            clean_s = s.strip().strip("`")
            lines.append(f"- `{clean_s}`")
    else:
        lines.append("- No specific skills requested.")
    lines.append("")

    raw_doc = "\n".join(lines)
    return redact_secrets(raw_doc)


def write_handoff_file(content: str, output_path: str = None) -> str:
    """Save handoff document to OS temp directory or explicit path."""
    if output_path:
        out = Path(output_path).resolve()
    else:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        tmp_dir = Path(tempfile.gettempdir())
        out = tmp_dir / f"handoff_{timestamp}.md"

    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(content)

    try:
        os.chmod(out, 0o600)
    except Exception:
        pass

    return str(out)


def main():
    parser = argparse.ArgumentParser(
        description="Zero-token Handoff Document Generator for AI Agent continuity."
    )
    parser.add_argument("--goal", "-g", default="Continue current task", help="Next session focus / objective")
    parser.add_argument("--title", "-t", default="Session Transition", help="Handoff title")
    parser.add_argument("--summary", default="", help="Executive summary of current session")
    parser.add_argument("--completed", default="", help="Semicolon-separated completed items")
    parser.add_argument("--decisions", default="", help="Semicolon-separated architectural decisions")
    parser.add_argument("--files", default="", help="Semicolon-separated modified or critical files")
    parser.add_argument("--blockers", default="", help="Semicolon-separated blockers or questions")
    parser.add_argument("--next-steps", default="", help="Semicolon-separated next actionable steps")
    parser.add_argument("--skills", "-s", default="", help="Comma-separated suggested skills")
    parser.add_argument("--output", "-o", help="Explicit output path (defaults to OS temp directory)")
    parser.add_argument("--print", "-p", action="store_true", help="Print document to stdout in addition to saving")

    args = parser.parse_args()

    cwd = os.getcwd()
    git_info = get_git_context(Path(cwd))

    metadata = {
        "title": args.title,
        "date": datetime.date.today().isoformat(),
        "next_session_focus": args.goal,
        "cwd": cwd,
        "git_branch": git_info["branch"],
        "git_commit": git_info["commit"],
    }

    sections = {
        "summary": args.summary or f"Session work focused on: {args.goal}.",
        "completed_work": args.completed,
        "key_decisions": args.decisions,
        "files_modified": args.files,
        "blockers": args.blockers,
        "next_steps": args.next_steps,
        "suggested_skills": args.skills,
    }

    doc = build_handoff_document(metadata, sections)
    saved_path = write_handoff_file(doc, args.output)

    print(f"Handoff document successfully generated at: {saved_path}")
    if args.print:
        print("\n" + "=" * 60)
        print(doc)
        print("=" * 60)


if __name__ == "__main__":
    main()
