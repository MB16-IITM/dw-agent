# src/tasks/a5.py
import logging
from pathlib import Path
from fastapi import HTTPException
from src.utils.security import validate_path, SecurityException
import json

logger = logging.getLogger(__name__)

def handle_a5(params: dict):
    try:
        # Get validated paths
        input_dir = validate_path(params.get('input_dir', '/data/logs'))
        output_file = validate_path(params.get('output_file', '/data/logs-recent.txt'))
        
        # Create directory if missing (Phase B2 compliant)
        input_dir.mkdir(parents=True, exist_ok=True)
        
        if not input_dir.is_dir():
            raise HTTPException(400, "Path is not a directory")
        
        # Find log files
        log_files = sorted(
            input_dir.glob(params.get('file_pattern', '*.log')),
            key=lambda f: -f.stat().st_mtime  # Newest first
        )[:10]

        # Process files
        results = []
        for file in log_files:
            try:
                with file.open('r') as f:
                    results.append(f.readline().strip())
            except Exception as e:
                logger.error(f"File read error: {file.name}")
                results.append(f"Error reading {file.name}")
        
        # Write output
        with output_file.open('w') as f:
            f.write('\n'.join(results))
            
        # return {"processed_files": len(results)}
    except PermissionError:
        raise HTTPException(403, "Directory access denied")