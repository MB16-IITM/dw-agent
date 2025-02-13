# src/tasks/a6.py
from pathlib import Path
import json
import logging
from src.utils.security import validate_path
from fastapi import HTTPException

logger = logging.getLogger(__name__)

def find_md_files(root_dir: Path) -> list[Path]:
    """Recursively find all .md files in specified directory"""
    try:
        return list(root_dir.rglob('*.md'))
    except Exception as e:
        logger.error(f"Error finding MD files: {str(e)}")
        raise

def extract_first_h1(file_path: Path) -> str:
    """Extract first H1 heading from markdown file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith('# '):
                    return stripped[2:].strip()
        return ''
    except UnicodeDecodeError:
        logger.error(f"Invalid text encoding in {file_path}")
        return ''
    except Exception as e:
        logger.error(f"Error reading {file_path}: {str(e)}")
        raise

def relative_path(full_path: Path) -> str:
    """Convert absolute path to /data/docs/relative string"""
    try:
        return str(full_path.relative_to(Path('/data/docs')))
    except ValueError as e:
        logger.error(f"Path validation failed: {str(e)}")
        raise

def generate_index(md_files: list[Path]) -> dict:
    """Create filename-to-title mapping"""
    index = {}
    for md_file in md_files:
        try:
            title = extract_first_h1(md_file)
            index[relative_path(md_file)] = title
        except Exception as e:
            logger.warning(f"Skipping {md_file}: {str(e)}")
            continue
    return index

def handle_a6(params: dict):
    """Main handler function for A6 task"""
    try:
        # Validate and resolve paths
        docs_dir = validate_path(params.get('input_dir', '/data/docs'))
        output_file = validate_path(params.get('output_file', '/data/docs/index.json'))
        
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate index data
        md_files = find_md_files(docs_dir)
        index_data = generate_index(md_files)
        
        # Write JSON output
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
            
        return {
            "status": "success",
            "files_processed": len(index_data),
            "output_path": str(output_file)
        }
        
    except HTTPException:
        raise  # Re-raise validated security exceptions
    except Exception as e:
        logger.error(f"A6 processing failed: {str(e)}")
        raise RuntimeError(f"Index generation failed: {str(e)}")