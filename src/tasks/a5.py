# src/tasks/a5.py
import logging
from pathlib import Path
from fastapi import HTTPException
from src.utils.security import validate_path, SecurityException
import json

logger = logging.getLogger(__name__)

# def handle_a5(params: dict):
#     """Process 10 most recent log files"""
#     try:
        
#         # Validate paths with security checks
#         input_dir = validate_path(params.get('input_dir', '/data/logs'))
#         output_file = validate_path(params.get('output_file', '/data/logs-recent.txt'))
        
#         # Create logs directory if missing
#         input_dir.mkdir(exist_ok=True)
        
#         if not input_dir.exists():
#             raise HTTPException(404, "Log directory not found")
#         if not input_dir.is_dir():
#             raise HTTPException(400, "Path is not a directory") 
#         # Get all log files with timestamps
#         log_files = [(f, f.stat().st_mtime) 
#                     for f in input_dir.rglob('*.log') 
#                     if f.is_file()]
        
#         if not log_files:
#             raise HTTPException(400, "No log files found in directory")

#         # Sort by modification time (newest first)
#         sorted_files = sorted(log_files, key=lambda x: -x[1])[:10]
        
#         # Collect first lines
#         results = []
#         for file_path, _ in sorted_files:
#             try:
#                 with open(file_path, 'r') as f:
#                     first_line = f.readline().strip()
#                     results.append(first_line or f"Empty line in {file_path.name}")
#             except Exception as e:
#                 logger.warning(f"Error reading {file_path.name}: {str(e)}")
#                 results.append(f"Error reading file: {file_path.name}")

#         # Write output
#         with open(output_file, 'w') as f:
#             f.write('\n'.join(results))
            
#         return {
#             "status": "processed",
#             "input_dir": str(input_dir),
#             "output_file": str(output_file),
#             "files_processed": len(sorted_files)
#         }
#     except SecurityException as se:  # Handle security errors
#         logger.error(f"Security violation: {str(se)}")
#         raise HTTPException(403, detail=str(se))
#     except PermissionError:
#         logger.error("Permissions denied for log directory")
#         raise HTTPException(403, "Permission denied for file access")
#     except Exception as e:
#         logger.error(f"A5 processing error: {str(e)}")
#         raise HTTPException(500, "Internal processing error")


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
            
        return {"processed_files": len(results)}
    except PermissionError:
        raise HTTPException(403, "Directory access denied")