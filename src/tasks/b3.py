# src/tasks/b3.py
import requests
import json
import time
from pathlib import Path
from src.utils.security import validate_url, validate_path
from fastapi import HTTPException
import logging
import subprocess

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_DELAYS = [1, 3, 5]  # Seconds between retries
MAX_RESPONSE_SIZE = 10 * 1024 * 1024  # 10MB

def handle_b3(params: dict):
    """Fetch data from API and save to specified path"""
    try:
        # Validate input parameters
        api_url = params.get('url')
        output_path = params.get('output_path', '/data/api-response')
        
        # Security validation (updated)
        validate_url(api_url)  # Now allows any HTTPS URL except dangerous patterns
        safe_path = validate_path(output_path).resolve()
        
        method = params.get('method', 'GET').upper()
        params = params.get('params', {})
        timeout = params.get('timeout', 10)  # Default 10 seconds timeout

        # Additional security headers
        headers = params.get('headers', {})
        headers.update({
            'User-Agent': 'DataWorks/1.0',
            'X-Request-Source': 'automation-agent'
        })
        
        # Execute API request with retries
        response = None
        for attempt in range(MAX_RETRIES):
            try:
                # Flush DNS cache between attempts
                subprocess.run(['nscd', '-i', 'hosts'], check=False)
                response = requests.request(
                    method=method,
                    url=api_url,
                    headers=headers,
                    params=params,
                    timeout=timeout,
                    stream=True  # Stream response for large files
                )
                response.raise_for_status()
                break
            except requests.exceptions.RequestException as e:
                if attempt < MAX_RETRIES - 1:
                    logger.warning(f"API request failed (attempt {attempt+1}): {str(e)}")
                    time.sleep(RETRY_DELAYS[attempt])
                else:
                    raise HTTPException(500, f"API request failed after {MAX_RETRIES} attempts: {str(e)}")

        # Determine output format
        content_type = response.headers.get('Content-Type', 'application/octet-stream')
        ext = get_extension(content_type)
        final_path = safe_path.with_suffix(ext)

        # Write response content with size validation
        with final_path.open('wb') as f:
            size = 0
            for chunk in response.iter_content(chunk_size=8192):
                size += len(chunk)
                if size > MAX_RESPONSE_SIZE:
                    raise HTTPException(413, "Response exceeds 10MB limit")
                f.write(chunk)

        return {"status": "success", "path": str(final_path)}

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"B3 execution failed: {str(e)}")
        raise HTTPException(500, f"API fetch failed: {str(e)}")

def get_extension(content_type: str) -> str:
    """Map content types to file extensions"""
    type_map = {
        'application/json': '.json',
        'text/csv': '.csv',
        'application/xml': '.xml',
        'text/plain': '.txt',
        'image/png': '.png',
        'image/jpeg': '.jpg'
    }
    return type_map.get(content_type.split(';')[0], '.bin')
