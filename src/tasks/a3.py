from datetime import datetime
from dateutil import parser
from pathlib import Path
from src.utils.security import validate_path
from fastapi import HTTPException


WEEKDAY_MAP = {
    'monday': 0, 'tuesday': 1, 'wednesday': 2,
    'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6
}

def handle_a3(params: dict):
    """Main handler for A3 tasks"""
    input_path = validate_path(params.setdefault("input_file", "/data/dates.txt"))
    output_path = validate_path(params.setdefault("output_file", "/data/day-count.txt"))
    target_weekday = WEEKDAY_MAP[params['weekday'].lower()]
    
    if not input_path.exists():
        raise HTTPException(400, detail=f"Input file {input_path} not found")

    # Ensure parent directories exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    count = 0
    with input_path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            try:
                dt = parser.parse(line, fuzzy=True, dayfirst=False)
                if dt.weekday() == target_weekday:
                    count += 1
            except (ValueError, OverflowError):
                continue
    
    output_path.write_text(str(count))
    return {"count": count, "output_path": str(output_path)}
