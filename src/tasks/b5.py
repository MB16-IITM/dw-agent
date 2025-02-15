# tasks/b5.py
import sqlite3
from pathlib import Path
from fastapi import HTTPException
from src.utils.security import validate_path, validate_sql, audit_sql_operation, OperationalError, SecurityException, validate_write_path

def execute_safe_query(db_path: str, query: str, params: list):
    """Execute parameterized SQL query with security checks"""
    try:
        # Validate database path
        db_path = validate_path(db_path)
        if not db_path.exists():
            raise HTTPException(404, "Database file not found")

        # Security validation
        validate_sql(query, params)
        
        with sqlite3.connect(f'file:{db_path}?mode=ro', uri=True) as conn:
            conn.execute("PRAGMA query_only = 1")  # Enforce read-only
            conn.execute("PRAGMA busy_timeout = 5000")  # 5s timeout
            
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            # Limit result size
            results = cursor.fetchmany(1000)
            
            audit_sql_operation(query, db_path)
            return results
            
    except OperationalError as oe:
        raise HTTPException(400, f"SQL execution error: {str(oe)}")
    except SecurityException as se:
        raise HTTPException(403, str(se))

def handle_b5(params: dict):
    required_params = ["db_path", "query", "output_file"]  # Add output_file
    if missing := [p for p in required_params if p not in params]:
        raise HTTPException(400, f"Missing parameters: {missing}")

    try:
        # Validate output path first
        output_path = validate_write_path(params["output_file"])
        
        # Execute query
        results = execute_safe_query(
            params["db_path"],
            params["query"],
            params.get("parameters", [])
        )
        
        # Write results to file
        with open(output_path, 'w') as f:
            if params["query"].lower().startswith("select"):
                if results and len(results[0]) == 1:  # Single column result
                    f.write(str(results[0][0]))
                else:
                    f.write('\n'.join(str(row) for row in results))
            else:
                f.write(str(len(results)))

        return {"status": "success", "output_file": str(output_path)}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(500, f"Query failed: {str(e)}")
