# services/dispatcher.py
from tools.remote_tool import RemoteTool
from config import settings
from models import MCPRequest, MCPResponse, MCPErrorResponse

# Build your tool registry from config
_TOOL_REGISTRY = {
    tool_cfg.name: RemoteTool(tool_cfg)
    for tool_cfg in settings.tools
}

async def dispatch(req: MCPRequest) -> dict:
    if req.method == "initialize":
        return MCPResponse(
            id=req.id,
            result={
                "protocolVersion": "2024-11-05",
                "capabilities": { "tools": {t.name: t.input_schema for t in _TOOL_REGISTRY.values()}},
                "serverInfo": { "name": "mcp-gateway", "version": "1.0.0" }
            }
        ).dict()

    if req.method == "tools/list":
        return MCPResponse(
            id=req.id,
            result={ "tools": [
                {
                  "name": t.name,
                  "description": t.description,
                  "inputSchema": t.input_schema
                } for t in _TOOL_REGISTRY.values()
            ]}
        ).dict()

    if req.method == "tools/call":
        params = req.params or {}
        name   = params.get("name")
        args   = params.get("arguments", {})
        tool   = _TOOL_REGISTRY.get(name)
        if not tool:
            return MCPErrorResponse(id=req.id, error={"code": -32601, "message": f"Tool '{name}' not found"}).dict()
        try:
            result = await tool.run(req.id, args)
            return MCPResponse(id=req.id, result=result).dict()
        except Exception as e:
            return MCPErrorResponse(id=req.id, error={"code": -32603, "message": str(e)}).dict()

    return MCPErrorResponse(id=req.id, error={"code": -32601, "message": f"Method '{req.method}' not found"}).dict()
