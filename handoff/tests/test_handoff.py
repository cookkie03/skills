#!/usr/bin/env python3
"""
Unit tests for Handoff Generator (TDD suite)
"""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Add scripts directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

try:
    from handoff_generator import (
        redact_secrets,
        get_git_context,
        build_handoff_document,
        write_handoff_file,
    )
except ImportError:
    pass


class TestHandoffSecretRedaction(unittest.TestCase):
    def test_redact_api_keys(self):
        sample = (
            "Connected with key sk-1234567890abcdef1234567890abcdef and "
            "GitHub token ghp_1234567890abcdef1234567890abcdef123456"
        )
        redacted = redact_secrets(sample)
        self.assertNotIn("sk-1234567890abcdef", redacted)
        self.assertNotIn("ghp_1234567890", redacted)
        self.assertIn("[REDACTED", redacted)

    def test_redact_bearer_tokens(self):
        sample = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.t-ID5pcTpQ"
        redacted = redact_secrets(sample)
        self.assertNotIn("eyJhbGciOi", redacted)
        self.assertIn("[REDACTED", redacted)

    def test_redact_key_value_passwords(self):
        sample = "DB_PASSWORD=my_super_secret_pw_123;\napiKey: 'secret_token_val_999'"
        redacted = redact_secrets(sample)
        self.assertNotIn("my_super_secret_pw_123", redacted)
        self.assertNotIn("secret_token_val_999", redacted)
        self.assertIn("[REDACTED", redacted)

    def test_redact_empty_and_none(self):
        self.assertEqual(redact_secrets(""), "")
        self.assertEqual(redact_secrets(None), "")

    def test_redact_multiple_mixed_tokens(self):
        sample = (
            "AWS: AKIAIOSFODNN7EXAMPLE, "
            "Slack: mockbot-1234567890-123456789012-abcdef1234567890abcdef12, "
            "Google: AIzaSyD1234567890abcdef1234567890abcdef"
        )
        redacted = redact_secrets(sample)
        self.assertNotIn("AKIAIOSFODNN7EXAMPLE", redacted)
        self.assertNotIn("mockbot-1234567890", redacted)
        self.assertNotIn("AIzaSyD1234567890", redacted)

    def test_preserve_safe_text(self):
        safe_text = "Refactored the authentication middleware in /src/auth/handler.py to support OAuth2."
        self.assertEqual(redact_secrets(safe_text), safe_text)


class TestHandoffGitContext(unittest.TestCase):
    def test_git_context_in_repo(self):
        repo_path = Path(__file__).resolve().parent
        context = get_git_context(repo_path)
        self.assertIsInstance(context, dict)
        self.assertIn("branch", context)
        self.assertIn("commit", context)

    def test_git_context_in_non_repo(self):
        non_repo = Path(tempfile.gettempdir())
        context = get_git_context(non_repo)
        self.assertIsInstance(context, dict)
        self.assertIn("branch", context)


class TestHandoffDocumentBuilder(unittest.TestCase):
    def test_document_sections(self):
        meta = {
            "title": "Handoff: Authentication Refactoring",
            "date": "2026-09-08",
            "next_session_focus": "Implement JWT validation middleware",
            "cwd": "/Users/luca/workspace/auth",
            "git_branch": "feature/auth-jwt",
            "git_commit": "a1b2c3d",
        }
        sections = {
            "summary": "Completed core schema and password hashing.",
            "completed_work": ["Implemented bcrypt hashing", "Added auth unit tests"],
            "key_decisions": ["Selected RS256 for asymmetric signing"],
            "files_modified": ["src/auth/hash.py", "tests/test_hash.py"],
            "blockers": ["Need public key configuration from ops"],
            "next_steps": ["Write JWT claim parser", "Add token expiry test"],
            "suggested_skills": ["python-testing", "git"],
        }
        doc = build_handoff_document(meta, sections)

        # Check YAML Frontmatter
        self.assertTrue(doc.startswith("---"))
        self.assertIn("type: \"Agent Handoff Document\"", doc)
        self.assertIn("next_session_focus: \"Implement JWT validation middleware\"", doc)

        # Check Mandatory Structural Sections
        self.assertIn("# Handoff Document: Authentication Refactoring", doc)
        self.assertIn("## 1. Executive Summary & Objective", doc)
        self.assertIn("## 2. Completed Work & Changes", doc)
        self.assertIn("## 3. Key Decisions & Rationale", doc)
        self.assertIn("## 4. Critical File Paths & Artifacts", doc)
        self.assertIn("## 5. Current State & Known Blockers", doc)
        self.assertIn("## 6. Actionable Next Steps for Incoming Agent", doc)
        self.assertIn("## 7. Suggested Skills for Incoming Agent", doc)

        # Check Content Integration
        self.assertIn("Implemented bcrypt hashing", doc)
        self.assertIn("src/auth/hash.py", doc)
        self.assertIn("`python-testing`", doc)


class TestHandoffFileWriter(unittest.TestCase):
    def test_write_to_temp_dir(self):
        content = "# Handoff Test\n\nSample content."
        filepath = write_handoff_file(content)
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(str(filepath).startswith(tempfile.gettempdir()) or "/tmp" in str(filepath))
        with open(filepath, "r") as f:
            self.assertEqual(f.read(), content)

    def test_write_to_explicit_path(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".md") as tmp:
            tmp_path = tmp.name
        try:
            content = "# Explicit Handoff Test\n\nSpecific path write."
            out = write_handoff_file(content, output_path=tmp_path)
            self.assertEqual(out, tmp_path)
            with open(tmp_path, "r") as f:
                self.assertEqual(f.read(), content)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


class TestHandoffCLI(unittest.TestCase):
    def test_cli_execution(self):
        script = Path(__file__).resolve().parent.parent / "scripts" / "handoff_generator.py"
        cmd = [
            sys.executable,
            str(script),
            "--goal", "Test next agent workflow",
            "--summary", "CLI testing executed",
            "--skills", "skill-creator, handoff",
            "--next-steps", "Review test output; Verify git status",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"CLI failed: {res.stderr}")
        self.assertIn("Handoff document successfully generated at:", res.stdout)


if __name__ == "__main__":
    unittest.main()
