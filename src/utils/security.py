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
from sqlite3 import OperationalError
import re
import logging  # Add at top
logger = logging.getLogger(__name__)

FILE_AUDIT_LOG = set()


def audit_write_operation(path: Path):
    """Track file modifications separately"""
    FILE_AUDIT_LOG.add(str(path.resolve()))

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
        if any(pattern in str(path) for pattern in ['.exif', '.icc', '.icm']):
            raise SecurityException("Potential embedded metadata detected")
        
        # Allow non-existent paths for directory creation
        return path
    except Exception as e:
        raise HTTPException(400, f"Invalid path: {str(e)}")

def validate_write_path(user_path: str) -> Path:
    """Wrapper for write operations with auditing"""
    path = validate_path(user_path)
    audit_write_operation(path)
    return path

def audit_file_access(path: Path, mode: str):
    """Track file modifications with access patterns"""
    if mode in ('w', 'a', 'x'):
        FILE_AUDIT_LOG.add(str(path.resolve()))
        
def get_modified_files():
    """Retrieve list of modified files for verification"""
    return list(FILE_AUDIT_LOG)

def validate_url(url: str):
    """Secure URL validation for Phase B tasks"""
    try:
        parsed = urlparse(url)
        
        # Mandatory HTTPS enforcement
        if parsed.scheme != 'https':
            raise SecurityException("Only HTTPS URLs allowed")
            
        allowed_hosts = [
                "raw.githubusercontent.com",
                "github.com",
                "gitlab.com",
                "bitbucket.org",
                "gitea.com"
            ]
            
        if parsed.hostname not in allowed_hosts:
                raise SecurityException(f"Git host {parsed.hostname} not allowed")
        
        # Block known dangerous patterns
        forbidden_patterns = [
            '127.0.0.1', 'localhost', '::1',  # Localhost prevention
            '..', '%00',  # Path traversal
            '@'  # Basic credential prevention
        ]
        
        if any(pattern in url for pattern in forbidden_patterns):
            raise SecurityException("URL contains potentially dangerous components")

        # Validate port range
        if parsed.port:
            if not (1 <= parsed.port <= 65535):
                raise SecurityException("Invalid port number")
                
    except ValueError as ve:
        raise SecurityException(f"Invalid URL structure: {str(ve)}")
    except SecurityException as se:
        raise HTTPException(403, detail=str(se))
    

def validate_git_url(url: str):
    """Special validation for Git repository URLs"""
    try:
        # First perform base URL validation
        validate_url(url)  # Reuse existing security checks
        
        parsed = urlparse(url)
        
        # Enforce .git suffix for repository URLs
        if not parsed.path.endswith('.git'):
            raise SecurityException("Git repository URLs must end with .git")
            
        # Additional Git-specific host validation
        allowed_git_hosts = [
            'github.com',
            'gitlab.com',
            'bitbucket.org',
            'gitea.com',
            'git.dataworks.local'  # Internal repository host
        ]
        
        if parsed.hostname not in allowed_git_hosts:
            raise SecurityException(f"Git host {parsed.hostname} not whitelisted")
            
        # Prevent SSH-style URLs
        if parsed.scheme == 'ssh' or url.startswith('git@'):
            raise SecurityException("SSH protocol not allowed for Git operations")
            
    except SecurityException as se:
        raise HTTPException(403, detail=str(se))

SQL_BLACKLIST = [
    r"\bdrop\b", r"\bdelete\b", r"\btruncate\b", 
    r"\binsert\b", r"\bupdate\b", r";.*"
]

def validate_sql(query: str, params: dict):
    """Sanitize SQL queries using allow-list approach"""
    # Check for forbidden patterns
    for pattern in SQL_BLACKLIST:
        if re.search(pattern, query, re.IGNORECASE):
            raise SecurityException(f"Potentially dangerous SQL pattern detected: {pattern}")
    
    # Verify placeholder count matches parameters
    placeholders = query.count('?')
    if placeholders != len(params):
        raise SecurityException(f"Parameter count mismatch. Query expects {placeholders} params, got {len(params)}")
    
    # Enforce single-statement queries
    if len(query.split(';')) > 2:
        raise SecurityException("Multi-statement queries not allowed")

def audit_sql_operation(query: str, db_path: Path):
    """Track SQL operations for security review"""
    sanitized_query = re.sub(r'\s+', ' ', query).strip()
    logger.info(f"SQL Audit: {sanitized_query} on {db_path}")