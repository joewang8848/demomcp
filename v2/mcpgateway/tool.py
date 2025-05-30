# tool.py - Simple Tool Management
import yaml
import httpx
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Global config and client (initialized when config is loaded)
_config = None
_client = None

def load_tool_config():
    """Load tool config from file"""
    global _config, _client
    
    try:
        with open("tool.yml", 'r') as f:
            _config = yaml.safe_load(f)
            
            # Initialize HTTP client with config
            http_config = _config.get("http", {})
            timeout = http_config.get("timeout", 30.0)
            _client = httpx.AsyncClient(timeout=timeout)
            
            tools = _config.get("tools", [])
            logger.info(f"Loaded {len(tools)} tools from tool.yml (timeout: {timeout}s)")
            return tools
            
    except FileNotFoundError:
        logger.error("tool.yml file not found")
        return []
    except Exception as e:
        logger.error(f"Failed to load tool config: {e}")
        return []

async def call_tool(endpoint: str, name: str, args: Dict[str, Any]) -> str:
    """Call remote tool"""
    if _client is None:
        raise Exception("HTTP client not initialized - load config first")
        
    payload = {"tool_name": name, "arguments": args, "request_id": 1}
    
    try:
        response = await _client.post(endpoint, json=payload)
        result = response.json()
        
        if result.get("isError"):
            raise Exception(result["content"][0]["text"])
        
        return result["content"][0]["text"]
    except Exception as e:
        raise Exception(f"Tool call failed: {e}")

def create_tool_func(tool_config):
    """Create tool function with proper signature"""
    name = tool_config["name"]
    endpoint = tool_config["endpoint"]
    description = tool_config["description"]
    schema = tool_config.get("input_schema", {})
    
    # Build parameter signature
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    params = []
    
    for prop_name, prop_def in properties.items():
        if prop_name in required:
            params.append(f"{prop_name}: str")
        else:
            default = prop_def.get("default", '""')
            if isinstance(default, str):
                default = f'"{default}"'
            params.append(f"{prop_name}: str = {default}")
    
    # Create function code
    func_code = f'''
async def {name}({", ".join(params)}) -> str:
    """{description}"""
    args = {{{", ".join([f'"{p}": {p}' for p in properties.keys()])}}}
    return await call_tool("{endpoint}", "{name}", args)
'''
    
    # Execute and return function
    namespace = {"call_tool": call_tool}
    exec(func_code, namespace)
    return namespace[name]

def register_all_tools(mcp) -> int:
    """Register all tools with MCP server"""
    tools = load_tool_config()
    count = 0
    
    for tool_config in tools:
        try:
            tool_func = create_tool_func(tool_config)
            mcp.tool()(tool_func)
            logger.info(f"Registered: {tool_config['name']}")
            count += 1
        except Exception as e:
            logger.error(f"Failed to register {tool_config.get('name')}: {e}")
    
    return count