# models/mcp.py - MCP Models
from pydantic import BaseModel
from typing import Dict, Any, Optional, Union

class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Union[int, str]
    method: str
    params: Optional[Dict[str, Any]] = None

class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Union[int, str]
    result: Optional[Dict[str, Any]] = None

class MCPErrorResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Union[int, str]
    error: Dict[str, Any]