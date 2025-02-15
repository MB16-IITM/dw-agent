import subprocess
from pathlib import Path
from src.utils.security import validate_path


def handle_a2(params: dict) -> tuple:
    try:
        # Validate path from LLM parameters
        file_path = validate_path(params.get('file_path', '/data/format.md'))
            
        result = subprocess.run(
            ["npx", "prettier@3.4.2", "--stdin-filepath", str(file_path)],
            check=True,
            timeout=15,
            cwd="/data",
            stdout=subprocess.DEVNULL  # Disable output capture
        )
        return ("", 200)
    except subprocess.CalledProcessError as e:
        return f"Formatting failed: {e.stderr}", 500
    except FileNotFoundError:
        return "format.md not found", 404
