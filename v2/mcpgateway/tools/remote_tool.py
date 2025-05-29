# tools/remote_tool.py - HTTP Client
import httpx
from typing import Dict, Any, Union

class RemoteTool:
    def __init__(self, config):
        self.name = config.name
        self.description = config.description
        self.input_schema = config.input_schema
        self.endpoint = config.endpoint

    async def run(self, rpc_id: Union[int, str], arguments: Dict[str, Any]) -> Dict[str, Any]:
        payload = {
            "tool_name": self.name,
            "arguments": arguments,
            "request_id": rpc_id
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self.endpoint, json=payload)
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}")
            
            result = response.json()
            
            if isinstance(result, dict) and result.get("error"):
                raise Exception(result["error"])
            
            return result