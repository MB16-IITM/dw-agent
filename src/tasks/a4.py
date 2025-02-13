# src/tasks/a4.py
import json
import logging
from pathlib import Path
from fastapi import HTTPException
from src.utils.security import validate_path

logger = logging.getLogger(__name__)

def handle_a4(params: dict):
    """Sort contacts by last_name then first_name and save to output file"""
    try:
        # Validate and resolve paths
        input_path = validate_path(params.setdefault("input_file", "/data/contacts.json"))
        output_path = validate_path(params.setdefault("input_file", "/data/sorted-contacts.json"))
        
        # Load contacts data
        with open(input_path, 'r') as f:
            contacts = json.load(f)
        
        # Validate JSON structure
        if not isinstance(contacts, list) or not all(isinstance(c, dict) for c in contacts):
            raise ValueError("Invalid contacts format - expected array of objects")
            
        # Sort with case-insensitive comparison
        sorted_contacts = sorted(
            contacts,
            key=lambda x: (
                x.get('last_name', '').lower(),
                x.get('first_name', '').lower()
            )
        )
        
        # Write sorted output
        with open(output_path, 'w') as f:
            json.dump(sorted_contacts, f, indent=2, ensure_ascii=False)
            
        return {
            "status": "sorted",
            "input_file": str(input_path),
            "output_file": str(output_path),
            "count": len(sorted_contacts)
        }
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Input file not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format in input file")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"A4 sorting error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal sorting error")
