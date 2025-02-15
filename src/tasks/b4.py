import subprocess
from pathlib import Path
from fastapi import HTTPException
from src.utils.security import validate_path, validate_git_url, SecurityException
import logging
import re
import os
from contextlib import contextmanager

@contextmanager
def cwd(path: Path):
    """Pure directory change without side effects"""
    origin = Path.cwd()
    try:
        os.chdir(path)
        yield
    finally: 
        os.chdir(origin)



logger = logging.getLogger(__name__)

SAFE_GIT_ARGS = [
    'clone', 'add', 'commit', 'status',
    'pull', 'push', 'diff', 'log'
]

def handle_b4(params: dict):
    try:
        # Validate inputs
        repo_url = params['repository_url']
        target_dir = params.get('target_directory', '')
        commit_msg = params['commit_message']
        file_patterns = params.get('file_patterns', ['.'])
        
        validate_git_url(repo_url)
        
        # Generate safe target directory name
        if not target_dir:
            repo_name = re.search(r'/([^/]+?)\.git$', repo_url).group(1)
            target_dir = f"/data/repos/{repo_name}"
        
        target_path = validate_path(target_dir)
        
        # Phase B1 compliance: Never clone outside /data
        if not str(target_path).startswith('/data/repos'):
            raise HTTPException(403, "Repository must be cloned under /data/repos")
        
        # Ensure directory exists
        target_path.mkdir(parents=True, exist_ok=True)
        
        # Execute Git operations
        if not is_git_installed():
            raise HTTPException(500, "Git is not available in the execution environment")
        
        # Clone repository (if not exists)
        if not (target_path / '.git').exists():
            run_git_command(['clone', '--depth', '1', repo_url, str(target_path)])
            
        with cwd(target_path):
            # Create files if they don't exist
            for pattern in file_patterns:
                file_path = target_path / pattern
                if not file_path.exists():
                    file_path.touch()
        # Stage changes
        with cwd(target_path):
            run_git_command(['add'] + file_patterns)
            
            # Create commit
            commit_output = run_git_command(
                ['commit', '-m', commit_msg],
                allow_empty=False
            )
            
        return {
            "status": "success",
            "commit_hash": extract_commit_hash(commit_output),
            "path": str(target_path)
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Git operations failed: {str(e)}")
        raise HTTPException(500, f"Git error: {str(e)}")

def run_git_command(args: list, allow_empty: bool = True):
    """Execute git command with security checks"""
    # Validate command arguments
    for arg in args:
        if any(char in arg for char in {';', '&', '|', '$'}):
            raise SecurityException("Invalid characters in git command")
    
    try:
        result = subprocess.run(
            ['git'] + args,
            check=True,
            capture_output=True,
            text=True,
            timeout=30  # Prevent hanging operations
        )
        
        if not allow_empty and "nothing to commit" in result.stderr:
            raise HTTPException(400, "No changes to commit")
            
        return result.stdout
        
    except subprocess.TimeoutExpired:
        raise HTTPException(504, "Git operation timed out")
    except subprocess.CalledProcessError as e:
        raise HTTPException(500, f"Git command failed: {e.stderr}")

def is_git_installed():
    try:
        subprocess.run(['git', '--version'], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def extract_commit_hash(commit_output: str):
    match = re.search(r'\b[0-9a-f]{7}\b', commit_output)
    return match.group(0) if match else None



