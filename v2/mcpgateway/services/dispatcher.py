# services/dispatcher.py - Request Router
from typing import Dict, Any
from tools.remote_tool import RemoteTool
from config import settings
from models.mcp import MCPRequest, MCPResponse, MCPErrorResponse

# Build tool registry
tools = {t.name: RemoteTool(t) for t in settings.tools}

async def dispatch(req: MCPRequest) -> Dict[str, Any]:
    
    if req.method == "initialize":
        return MCPResponse(
            id=req.id,
            result={
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "mcp-gateway", "version": "2.0.0"}
            }
        ).dict()

    elif req.method == "tools/list":
        tool_list = [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_schema
            }
            for tool in tools.values()
        ]
        return MCPResponse(id=req.id, result={"tools": tool_list}).dict()

    elif req.method == "tools/call":
        if not req.params:
            return MCPErrorResponse(
                id=req.id, 
                error={"code": -32602, "message": "Missing parameters"}
            ).dict()

        tool_name = req.params.get("name")
        arguments = req.params.get("arguments", {})
        
        tool = tools.get(tool_name)
        if not tool:
            return MCPErrorResponse(
                id=req.id,
                error={"code": -32601, "message": f"Tool '{tool_name}' not found"}
            ).dict()

        try:
            result = await tool.run(req.id, arguments)
            return MCPResponse(id=req.id, result=result).dict()
        except Exception as e:
            return MCPErrorResponse(
                id=req.id,
                error={"code": -32603, "message": str(e)}
            ).dict()

    else:
        return MCPErrorResponse(
            id=req.id,
            error={"code": -32601, "message": f"Method '{req.method}' not found"}
        ).dict()