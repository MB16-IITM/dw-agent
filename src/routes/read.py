from fastapi import APIRouter, Query, HTTPException
from pathlib import Path
from src.utils.security import validate_path
from fastapi.responses import PlainTextResponse

router = APIRouter()

# @router.get("/read")
# async def read_file(path: str = Query(...)):
#     try:
#         full_path = validate_path(path)
#         return {"content": full_path.read_text()}
#     except FileNotFoundError:
#         raise HTTPException(404)

@router.get("/read")
async def read_file(path: str = Query(...)):
    try:
        full_path = Path(path)
        content = full_path.read_text()
        return PlainTextResponse(content)
    except PermissionError:
        raise HTTPException(403, detail="Path not allowed")
    except FileNotFoundError:
        raise HTTPException(404)
    except IsADirectoryError:
        raise HTTPException(400, detail="Path is a directory")

