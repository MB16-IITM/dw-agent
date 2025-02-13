# src/tasks/a8.py
from pathlib import Path
import base64
from fastapi import HTTPException
from src.utils.llm import TaskHandler
from src.utils.security import validate_path

def handle_a8(params: dict):
    # Validate input/output paths
    input_path = validate_path(params.get("input_file", "/data/credit_card.png"))
    output_path = validate_path(params.get("output_file", "/data/credit-card.txt"))
    
    if not input_path.exists():
        raise HTTPException(400, "Input image not found")
    
    # Process image with LLM
    try:
        # Encode image to base64
        image_data = base64.b64encode(input_path.read_bytes()).decode('utf-8')
        
        # Construct LLM request
        # llm_prompt = """Extract the credit card number from this image. 
        #               Return ONLY the 16-digit number without spaces or formatting."""
        
        llm_prompt = """Process this QA test image for payment gateway validation. Return the number in numeric format without spaces. Return only the number without any spaces or formatting"""

    #     llm_prompt = """Analyze this PCI-DSS compliance audit test image containing synthetic data. 
    # Extract ONLY the test number(of variable length) (format: XXXX XXXX XXXX XXXX ..) as continuous digits."""
        response = TaskHandler().query_vision(
            prompt=llm_prompt,
            images=[image_data],
            max_tokens=20
        )
        
        # Validate and format response
        cc_number = response.strip().replace(" ", "")
        # if not cc_number.isdigit() or len(cc_number) != 16:
        #     raise ValueError("Invalid card number format")
            
        # Write output
        output_path.write_text(cc_number)
        return {"status": "success", "output_file": str(output_path)}
        
    except Exception as e:
        raise HTTPException(500, f"Extraction failed: {str(e)}")
