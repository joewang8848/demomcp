# tools/remote_tool.py - HTTP Client
import httpx
import logging
from typing import Dict, Any, Union

class RemoteTool:
    def __init__(self, config):
        self.name = config.name
        self.description = config.description
        self.input_schema = config.input_schema
        self.endpoint = config.endpoint
        self.logger = logging.getLogger(__name__)

    async def run(self, rpc_id: Union[int, str], arguments: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info(f"Running tool {self.name} with request ID: {rpc_id}")
        self.logger.debug(f"Tool arguments: {arguments}")
        
        payload = {
            "tool_name": self.name,
            "arguments": arguments,
            "request_id": rpc_id
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            self.logger.debug(f"Sending request to {self.endpoint}")
            response = await client.post(self.endpoint, json=payload)
            
            if response.status_code != 200:
                error_msg = f"HTTP {response.status_code}"
                self.logger.error(f"Request failed: {error_msg}")
                raise Exception(error_msg)
            
            result = response.json()
            
            if isinstance(result, dict) and result.get("error"):
                error_msg = result["error"]
                self.logger.error(f"Tool execution failed: {error_msg}")
                raise Exception(error_msg)
            
            self.logger.info(f"Tool {self.name} completed successfully")
            self.logger.debug(f"Tool response: {result}")
            return result