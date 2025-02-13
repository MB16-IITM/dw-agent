# # src/utils/security.py
# from pathlib import Path
# from urllib.parse import urlparse
# from fastapi import HTTPException

# class SecurityException(Exception):
#     """Security violation exception with detailed message"""
#     def __init__(self, message="Security violation"):
#         super().__init__(message)

# DATA_ROOT = Path("/data").resolve()

# def validate_path(user_path: str) -> Path:
#     """
#     Universal path validation with security layers:
#     1. Null byte prevention
#     2. Path normalization
#     3. Directory traversal protection
#     4. Hidden file prevention
#     5. Strict DATA_ROOT containment
#     """
#     try:
#         # 1. Input sanitization
#         if '\0' in user_path:
#             raise SecurityException("Null bytes prohibited")
            
#         # 2. Normalize path format
#         clean_path = user_path.lstrip('/').replace('data/', '', 1)
#         if not clean_path:  # Handle root requests
#             clean_path = '.'

#         # 3. Create absolute path
#         absolute_path = (DATA_ROOT / clean_path).resolve()

#         # 4. Security checks
#         if not absolute_path.is_relative_to(DATA_ROOT):
#             raise SecurityException(f"Path traversal attempt: {user_path}")
            
#         if any(part.startswith('.') for part in absolute_path.parts):
#             raise SecurityException("Hidden files prohibited")

#         return absolute_path

#     except SecurityException as se:
#         raise HTTPException(403, detail=str(se))
#     except Exception as e:
#         raise HTTPException(400, detail=f"Invalid path: {str(e)}")



# # WORKS BUT NO SECURITY
# # def validate_path(user_path: str) -> Path:
# #     if not user_path.startswith('/data/'):
# #         raise ValueError(f"Invalid path prefix: {user_path}")
# #     user_path = Path("./"+user_path)
# #     return user_path

# Replace existing DATA_ROOT with:
# BASE_ROOT = Path("/app/data").resolve()
# DEV_MODE = os.getenv('DEV_MODE', 'false').lower() == 'true'










# def validate_path(user_path: str) -> Path:
#     try:
#         path = Path(user_path).resolve(strict=True)
#         if not path.is_relative_to(BASE_ROOT):
#             raise SecurityException(f"Path escapes {BASE_ROOT}")
#         return path
#     except FileNotFoundError:
#         raise HTTPException(404, "File not found")







# src/utils/security.py (updated)
from pathlib import Path
from urllib.parse import urlparse
from fastapi import HTTPException
import os

from pathlib import Path
from fastapi import HTTPException

class SecurityException(Exception):
    def __init__(self, message="Security violation"):
        super().__init__(message)

BASE_ROOT = Path("/data").resolve()

def validate_path(user_path: str) -> Path:
    try:
        path = Path(user_path).resolve()
        
        # Phase B1 compliance
        if not path.is_relative_to(Path('/data')):
            raise SecurityException(f"Path {path} escapes /data")
            
        # Allow non-existent paths for directory creation
        return path
    except Exception as e:
        raise HTTPException(400, f"Invalid path: {str(e)}")

def validate_url(url: str):
    """Secure URL validation for Phase B tasks"""
    try:
        parsed = urlparse(url)
        
        if parsed.scheme != 'https':
            raise SecurityException("Only HTTPS URLs allowed")
            
        allowed_domains = [
            'raw.githubusercontent.com',
            'api.dataworks.com',
            'git.dataworks.local'
        ]
        if parsed.netloc not in allowed_domains:
            raise SecurityException(f"Domain {parsed.netloc} not allowed")
            
        if '..' in parsed.path or '%00' in parsed.path:
            raise SecurityException("URL path traversal attempt")
    except SecurityException as se:
        raise HTTPException(403, detail=str(se))
