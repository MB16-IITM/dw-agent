from pathlib import Path
from fastapi import HTTPException
from src.utils.security import validate_path
from src.utils.llm import AI_PROXY_BASE, AIPROXY_TOKEN
import requests
import logging
import os

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Extract ONLY the sender's email address from this email. 
Return exactly the email address with no additional text or formatting."""

def handle_a7(params: dict):
    try:
        # Validate and resolve paths
        input_path = validate_path(params.get('input_file', '/data/email.txt'))
        output_path = validate_path(params.get('output_file', '/data/email-sender.txt'))
        
        # Verify input file exists
        if not input_path.exists():
            raise HTTPException(404, "Input file not found")
            
        # Read email content
        email_content = input_path.read_text()
        
        # Call LLM through AI Proxy
        response = requests.post(
            f"{AI_PROXY_BASE}/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('AIPROXY_TOKEN')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": email_content}
                ],
                "temperature": 0.1
            },
            timeout=10
        )
        
        # Handle API errors
        response.raise_for_status()
        
        # Extract and validate response
        email = response.json()['choices'][0]['message']['content'].strip()
        if '@' not in email or ' ' in email:
            raise ValueError("Invalid email format received")
            
        # Write validated output
        output_path.write_text(email)
        # return {"status": "success", "output_file": str(output_path)}
        
    except requests.exceptions.RequestException as e:
        logger.error(f"LLM API error: {str(e)}")
        raise HTTPException(500, "Email extraction service unavailable")
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"A7 failed: {str(e)}")
        raise HTTPException(500, f"Email extraction failed: {str(e)}")
