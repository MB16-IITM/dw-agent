import subprocess
from pathlib import Path
from src.utils.security import validate_path


def handle_a2(params: dict) -> tuple:
    try:
        # Validate path from LLM parameters
        raw_path = params.get('file_path')
        if not raw_path:
            file_path = Path("/data/format.md")
            
        file_path = validate_path(raw_path)
            
        result = subprocess.run(
            ["prettier", "--write", str(file_path.absolute()), "--config", "/app/.prettierrc"],
            capture_output=True,
            text=True,
            check=True,
            timeout=15,
            cwd="/data"
        )
        # Sanitize output path
        clean_output = result.stdout.replace('../', '')
        return clean_output, 200
    except subprocess.CalledProcessError as e:
        return f"Formatting failed: {e.stderr}", 500
    except FileNotFoundError:
        return "format.md not found", 404
