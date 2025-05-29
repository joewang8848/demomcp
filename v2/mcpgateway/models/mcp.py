# models/mcp.py - MCP Models (Fixed)
from pydantic import BaseModel
from typing import Dict, Any, Optional, Union

class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[Union[int, str]] = None  # Optional for notifications
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