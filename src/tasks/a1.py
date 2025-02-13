# src/tasks/a1.py
import os
import requests
import subprocess
from pathlib import Path
from src.utils.security import validate_url
import sys

SCRIPT_URL = "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py"
DEFAULT_EMAIL = "24f1001631@ds.study.iitm.ac.in"


def handle_a1(params: dict):
    """Execute datagen.py directly from GitHub using uv"""
    try:
        # Verify UV installation
        subprocess.run(["uv", "--version"], 
                      check=True,
                      stdout=subprocess.DEVNULL,
                      stderr=subprocess.DEVNULL)
    except (FileNotFoundError, subprocess.CalledProcessError):
        # Install UV if missing
        subprocess.run([sys.executable, "-m", "pip", "install", "uv"],
                      check=True)
    email = params.get("user_email", DEFAULT_EMAIL).strip()
    
    try:
        validate_url(SCRIPT_URL)
        
        # Direct execution from URL with output directory
        result = subprocess.run(
            ["uv", "run", SCRIPT_URL, email, "--root", "/data"],
            capture_output=True,
            text=True,
            check=True,
            timeout=20
        )
        
        return result.stdout
        
    except subprocess.CalledProcessError as e:
        return f"Execution failed: {e.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"