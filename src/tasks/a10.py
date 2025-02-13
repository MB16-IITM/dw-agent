import sqlite3
from fastapi import HTTPException
from pathlib import Path
from src.utils.security import validate_path

def handle_a10(params: dict):
    try:
        db_path = validate_path(params.get('db_path', '/data/ticket-sales.db'))
        output_file = validate_path(params.get('output_file', '/data/ticket-sales-gold.txt'))
        
        with sqlite3.connect(str(db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(units * price) FROM tickets WHERE type=?", ('Gold',))
            total = cursor.fetchone()[0] or 0
            
        output_file.write_text(str(total))
        return {"status": "success", "total_sales": total}
        
    except sqlite3.Error as e:
        raise HTTPException(500, f"Database error: {str(e)}")
    except PermissionError:
        raise HTTPException(403, "File access denied")
