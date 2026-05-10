"""Agent wrapper for spawning coding agents"""
import json
import subprocess
from typing import Optional

def spawn_agent(
    task: str,
    agent: str = "gemini",
    workspace: str = None,
    timeout: int = 600
) -> dict:
    """Spawn a coding agent to execute a task.
    
    Args:
        task: Task description
        agent: Agent to use (gemini, codex)
        workspace: Working directory
        timeout: Timeout in seconds
    
    Returns:
        dict with status and output
    """
    workspace = workspace or "/home/luca/.openclaw/workspace"
    
    if agent == "gemini":
        cmd = ["gemini", "-p", task]
    elif agent == "codex":
        cmd = ["codex", "exec", task]
    else:
        return {"status": "error", "message": f"Unknown agent: {agent}"}
    
    try:
        result = subprocess.run(
            cmd,
            cwd=workspace,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return {
            "status": "success" if result.returncode == 0 else "error",
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "message": f"Task timed out after {timeout}s"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def list_available_agents() -> list:
    """List available agents."""
    agents = []
    
    # Check Gemini
    try:
        subprocess.run(["gemini", "--version"], capture_output=True, timeout=5)
        agents.append({"name": "gemini", "status": "available"})
    except:
        pass
    
    # Check Codex
    try:
        subprocess.run(["codex", "--version"], capture_output=True, timeout=5)
        agents.append({"name": "codex", "status": "needs_api_key"})
    except:
        pass
    
    return agents
