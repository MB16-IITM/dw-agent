from fastapi import HTTPException
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any
import json
from src.utils.security import validate_write_path

def handle_b6(params: Dict[str, Any]):
    try:
        # Validate input parameters
        if not params.get("url") or not params.get("output_file"):
            raise HTTPException(400, "Missing required parameters: url and output_file")
            
        # Security validation
        output_path = validate_write_path(params["output_file"])
        url = params["url"]

        # Scraping logic
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = {}

        # Extract elements based on CSS selectors
        if params.get("selectors"):
            for selector in params["selectors"]:
                elements = soup.select(selector)
                results[selector] = [element.get_text(strip=True) for element in elements]
        else:
            # Default extraction if no selectors provided
            results = {
                "title": [soup.title.string] if soup.title else [],
                "paragraphs": [p.get_text(strip=True) for p in soup.select('p')]
            }

        # Write results to file
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)

        return {"status": "success", "output_file": str(output_path)}
        
    except requests.RequestException as e:
        raise HTTPException(500, f"Scraping failed: {str(e)}")
    except Exception as e:
        raise HTTPException(500, f"Unexpected error: {str(e)}")
