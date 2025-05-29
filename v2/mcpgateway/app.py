# main.py - MCP Gateway (Fixed)
from fastapi import FastAPI, Request
from models.mcp import MCPRequest
from services.dispatcher import dispatch
from config import settings
from utils.logger import setup_logging

setup_logging()

app = FastAPI(title="MCP Gateway", version="2.0.0")

@app.post(settings.rpc_path)
async def mcp_endpoint(request: Request):
    body = await request.json()
    req = MCPRequest(**body)
    result = await dispatch(req)
    
    # Return empty response for notifications (no id)
    if result is None:
        return {}
    
    return result

@app.get("/health")
async def health():
    return {"status": "healthy", "tools": len(settings.tools)}

@app.get("/tools")
async def list_tools():
    return {"tools": [{"name": t.name, "endpoint": t.endpoint} for t in settings.tools]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.server.host, port=settings.server.port)