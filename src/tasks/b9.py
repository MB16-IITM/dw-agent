# src/tasks/b9.py
from pathlib import Path
import markdown
from src.utils.security import validate_path, validate_write_path
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

def handle_b9(params: dict):
    try:
        # Validate paths using security module
        input_path = validate_path(params['input_file'])
        output_path = validate_write_path(params['output_file'])
        
        # Ensure file types
        if input_path.suffix != '.md':
            raise HTTPException(400, "Input must be a .md file")
        if output_path.suffix != '.html':
            raise HTTPException(400, "Output must be .html")
            
        # Read Markdown content
        try:
            with open(input_path, 'r') as md_file:
                markdown_content = md_file.read()
        except FileNotFoundError:
            raise HTTPException(404, f"Markdown file not found: {input_path}")

        # Convert to HTML
        html_content = markdown.markdown(markdown_content)
        
        # Write HTML output
        try:
            with open(output_path, 'w') as html_file:
                html_file.write(html_content)
                logger.info(f"Converted {input_path} to {output_path}")
        except IOError as e:
            raise HTTPException(500, f"Failed to write HTML: {str(e)}")

        return {"status": "success", "input": str(input_path), "output": str(output_path)}
    
    except Exception as e:
        logger.error(f"B9 Conversion failed: {str(e)}")
        raise HTTPException(500, f"Conversion error: {str(e)}")
