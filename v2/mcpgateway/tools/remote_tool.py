# tools/remote_tool.py
import httpx
from .base import BaseTool
from models import MCPResponse, MCPErrorResponse

class RemoteTool(BaseTool):
    def __init__(self, config):
        self.name = config.name
        self.description = config.description
        self.input_schema = config.input_schema
        self.url = config.endpoint

    async def run(self, rpc_id, arguments) -> dict:
        payload = {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "method": "tools/call",
            "params": {
                "name": self.name,
                "arguments": arguments
            }
        }
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(self.url, json=payload)
            resp.raise_for_status()
            data = resp.json()

        if "error" in data:
            # map JSON-RPC error into your MCPErrorResponse if you like
            raise Exception(data["error"]["message"])
        return data["result"]
