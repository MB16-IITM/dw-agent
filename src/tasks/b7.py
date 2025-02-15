from PIL import Image, ImageFile
from pathlib import Path
from fastapi import HTTPException
from src.utils.security import validate_path, validate_write_path
import logging

logger = logging.getLogger(__name__)
ImageFile.LOAD_TRUNCATED_IMAGES = True  # Handle corrupted images

SUPPORTED_FORMATS = ['JPEG', 'PNG', 'WEBP']
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB

def handle_b7(params: dict):
    try:
        # Validate paths
        in_path = validate_path(params['input_path'])
        out_path = validate_write_path(params['output_path'])
        
        if not in_path.exists():
            raise HTTPException(400, f"Input image {in_path} not found")
            
        if in_path.stat().st_size > MAX_IMAGE_SIZE:
            raise HTTPException(400, f"Image exceeds 10MB limit")

        # Process image
        with Image.open(in_path) as img:
            # Resize logic
            if 'width' in params or 'height' in params:
                w, h = calculate_new_size(
                    original_size=img.size,
                    target_width=params.get('width'),
                    target_height=params.get('height'),
                    preserve_aspect=params.get('preserve_aspect', True)
                )
                img = img.resize((w, h), Image.LANCZOS)

            # Save with quality setting
            output_format = Path(out_path).suffix[1:].upper()
            if output_format not in SUPPORTED_FORMATS:
                raise HTTPException(400, f"Unsupported format: {output_format}")

            save_args = {
                'format': output_format,
                'quality': params.get('quality', 85),
                'optimize': True
            }
            
            if output_format == 'PNG':
                save_args['compress_level'] = 3
                
            img.save(out_path, **save_args)
            
        return {"status": "success", "output_path": str(out_path)}

    except IOError as e:
        logger.error(f"Image processing failed: {str(e)}")
        raise HTTPException(500, "Image processing error")

def calculate_new_size(original_size, target_width=None, target_height=None, preserve_aspect=True):
    orig_width, orig_height = original_size
    
    if not preserve_aspect:
        return (
            target_width or orig_width, 
            target_height or orig_height
        )

    # Aspect ratio preserving calculation
    if target_width and target_height:
        return (target_width, target_height)
        
    ratio = orig_width / orig_height
    
    if target_width:
        return (target_width, int(target_width / ratio))
        
    if target_height:
        return (int(target_height * ratio), target_height)
    
    return original_size
