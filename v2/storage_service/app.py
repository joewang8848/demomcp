# app.py - File Storage Service
import os
import uuid
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

app = FastAPI()

# Storage directory
STORAGE_DIR = Path("./storage")
STORAGE_DIR.mkdir(exist_ok=True)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file and return UUID"""
    try:
        # Generate UUID and preserve file extension
        file_uuid = str(uuid.uuid4())
        file_ext = Path(file.filename).suffix if file.filename else ""
        new_filename = f"{file_uuid}{file_ext}"
        
        # Save file
        file_path = STORAGE_DIR / new_filename
        content = await file.read()
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        return {
            "uuid": file_uuid,
            "filename": new_filename,
            "original_name": file.filename,
            "size": len(content),
            "download_url": f"http://192.168.4.154:8002/download/{file_uuid}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/download/{file_uuid}")
async def download_file(file_uuid: str):
    """Download file by UUID"""
    try:
        # Find file with this UUID (check all extensions)
        files = list(STORAGE_DIR.glob(f"{file_uuid}.*"))
        
        if not files:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_path = files[0]
        return FileResponse(
            path=file_path,
            filename=file_path.name,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@app.get("/list")
async def list_files():
    """List all stored files"""
    files = []
    for file_path in STORAGE_DIR.iterdir():
        if file_path.is_file():
            uuid_part = file_path.stem
            files.append({
                "uuid": uuid_part,
                "filename": file_path.name,
                "size": file_path.stat().st_size
            })
    return {"files": files, "count": len(files)}

@app.get("/health")
async def health():
    return {"status": "healthy", "storage_dir": str(STORAGE_DIR)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)