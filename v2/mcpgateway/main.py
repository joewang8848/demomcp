# main.py
from fastapi import FastAPI, Request
from models import MCPRequest
from services.dispatcher import dispatch
from config import settings
from logger import init_logging

init_logging()  # your centralized logger setup

app = FastAPI(openapi_prefix=settings.rpc_path)

@app.post(settings.rpc_path)
async def mcp_endpoint(raw: Request):
    body = await raw.json()
    req  = MCPRequest(**body)
    return await dispatch(req)

@app.get("/ping")
async def ping():
    return {"pong": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
