# app.py - SQL Generator Tool (Script Generation Version)
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any, Union
import base64

app = FastAPI()

class ToolRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    request_id: Union[int, str]

@app.post("/v1/generate_sql_files")
async def generate_sql_files(request: ToolRequest):
    try:
        streamid = request.arguments.get("streamid")
        sql_content = request.arguments.get("sql_content")
        
        if not streamid or not sql_content:
            return {"content": [{"type": "text", "text": "Missing streamid or sql_content"}], "isError": True}
        
        # Generate .jil file content
        jil_content = f"""-- Stream ID: {streamid}
-- Generated JIL file
-- This file contains metadata for stream: {streamid}

STREAM_ID={streamid}
GENERATED_AT=${{timestamp}}
FILE_TYPE=JIL
"""
        
        # Generate main.sql content (use the provided SQL)
        main_sql_content = f"""-- Main SQL file for stream: {streamid}
-- Generated automatically

{sql_content}
"""
        
        # Create executable script
        script_content = f"""#!/bin/bash
# Auto-generated script to create SQL files for stream: {streamid}

echo "Creating directories..."
mkdir -p jil
mkdir -p sql

echo "Creating JIL file..."
cat > ./jil/{streamid}.jil << 'JIL_EOF'
{jil_content}
JIL_EOF

echo "Creating SQL file..."
cat > ./sql/main.sql << 'SQL_EOF'
{main_sql_content}
SQL_EOF

echo "✅ Files created successfully:"
echo "   - ./jil/{streamid}.jil"
echo "   - ./sql/main.sql"
echo ""
echo "File contents:"
echo "📄 JIL file size: $(wc -c < ./jil/{streamid}.jil) bytes"
echo "📄 SQL file size: $(wc -c < ./sql/main.sql) bytes"
"""
        
        result_text = f"""📁 Generated SQL files for stream: {streamid}

🤖 GITHUB COPILOT: Please create and execute the following script:

SCRIPT_NAME: create_sql_files_{streamid}.sh
SCRIPT_CONTENT:
{script_content}

MANUAL_STEPS (if script doesn't work):
1. mkdir -p jil sql
2. Create ./jil/{streamid}.jil with JIL metadata
3. Create ./sql/main.sql with your SQL queries

📄 PREVIEW:
JIL File: ./jil/{streamid}.jil ({len(jil_content)} chars)
SQL File: ./sql/main.sql ({len(main_sql_content)} chars)
"""
        
        return {
            "content": [{"type": "text", "text": result_text}], 
            "isError": False,
            "executable_script": {
                "filename": f"create_sql_files_{streamid}.sh",
                "content": script_content,
                "instructions": "Save this script and run: chmod +x create_sql_files_{streamid}.sh && ./create_sql_files_{streamid}.sh"
            },
            "files": {
                f"jil/{streamid}.jil": jil_content,
                "sql/main.sql": main_sql_content
            }
        }
        
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error: {str(e)}"}], "isError": True}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9002)