#!/usr/bin/env python3
"""Refresh configured third-party skill snapshots without touching other repo paths."""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / ".notion-sync" / "sources.json"


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def copy_skill_tree(source_dir: Path, target_dir: Path) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    for item in source_dir.rglob("*"):
        if item.is_symlink():
            continue
        if any(part in {".git", "__pycache__"} for part in item.relative_to(source_dir).parts):
            continue
        if item.name == ".DS_Store":
            continue
        relative = item.relative_to(source_dir)
        destination = target_dir / relative
        if item.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
        elif item.is_file():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, destination)


def sync_source(source: dict) -> int:
    repo_url = source["repo"]
    branch = source.get("branch", "main")
    includes = source["include"]
    path_prefix = Path(source.get("source_path_prefix", "."))
    destination = ROOT / source["destination"]
    source_id = source["id"]

    with tempfile.TemporaryDirectory(prefix="skills-upstream-") as temp:
        checkout = Path(temp) / "checkout"
        stage = Path(temp) / "stage"
        run([
            "git", "clone", "--depth", "1", "--filter=blob:none", "--sparse",
            "--single-branch", "--branch", branch, repo_url, str(checkout),
        ])
        run(["git", "-C", str(checkout), "sparse-checkout", "set", *includes])

        count = 0
        for include in includes:
            include_path = checkout / include
            if not include_path.exists():
                continue
            # Each selected category contains skill folders directly. Keep traversal
            # at this level to avoid accidentally nesting one skill inside another.
            for skill_dir in sorted(include_path.iterdir()):
                skill_file = skill_dir / "SKILL.md"
                if skill_dir.is_symlink() or not skill_dir.is_dir():
                    continue
                if not skill_file.is_file() or skill_file.is_symlink():
                    continue
                relative = skill_dir.relative_to(checkout / path_prefix)
                target = stage / relative
                copy_skill_tree(skill_dir, target)
                count += 1

        if count == 0:
            raise RuntimeError(
                f"{source_id}: no SKILL.md files found in configured paths; "
                "keeping the existing third-party snapshot untouched."
            )

        staged_skills = list(stage.rglob("SKILL.md"))
        if len(staged_skills) != count:
            raise RuntimeError(f"{source_id}: staged skill count validation failed.")

        # The configured destination is a dedicated upstream mirror. Replacing only
        # this directory propagates upstream moves and deletions without touching
        # personal skills or other third-party sources.
        if destination.exists():
            shutil.rmtree(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(stage, destination)

    print(f"{source_id}: refreshed {count} skills into {source['destination']}")
    return count


def main() -> None:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    sources = config.get("sources", [])
    if not sources:
        raise RuntimeError("No third-party sources configured.")

    total = 0
    for source in sources:
        total += sync_source(source)

    print(f"Third-party refresh complete: {total} skills across {len(sources)} sources.")


if __name__ == "__main__":
    main()
