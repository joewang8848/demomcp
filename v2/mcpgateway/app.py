# app.py - Dynamic MCP Gateway with FastMCP + SSE  
import httpx
import yaml
from fastmcp import FastMCP
from typing import Dict, Any, get_type_hints
import inspect

# Load config
with open("config.yaml", 'r') as f:
    config = yaml.safe_load(f)

# Create MCP server
mcp = FastMCP("MCP Gateway")

# HTTP client for remote tools
client = httpx.AsyncClient(timeout=30.0)

async def call_tool(endpoint: str, name: str, args: Dict[str, Any]) -> str:
    """Call remote tool"""
    payload = {"tool_name": name, "arguments": args, "request_id": 1}
    response = await client.post(endpoint, json=payload)
    result = response.json()
    
    if result.get("isError"):
        raise Exception(result["content"][0]["text"])
    
    return result["content"][0]["text"]

def create_dynamic_tool(tool_config):
    """Create a tool function with proper signature from config"""
    tool_name = tool_config["name"]
    description = tool_config["description"]
    endpoint = tool_config["endpoint"]
    schema = tool_config.get("input_schema", {})
    
    # Build function signature dynamically
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    
    # Create parameter list for exec
    params = []
    param_docs = []
    
    for prop_name, prop_def in properties.items():
        prop_type = "str"  # Default type
        if prop_def.get("type") == "integer":
            prop_type = "int"
        elif prop_def.get("type") == "number":
            prop_type = "float"
        elif prop_def.get("type") == "boolean":
            prop_type = "bool"
        
        if prop_name in required:
            params.append(f"{prop_name}: {prop_type}")
        else:
            default = prop_def.get("default", '""' if prop_type == "str" else "None")
            if prop_type == "str" and isinstance(default, str):
                default = f'"{default}"'
            params.append(f"{prop_name}: {prop_type} = {default}")
        
        param_docs.append(f"    {prop_name}: {prop_def.get('description', 'No description')}")
    
    # Create function code
    func_code = f'''
async def {tool_name}({", ".join(params)}) -> str:
    """
    {description}
    
    Args:
{chr(10).join(param_docs)}
    """
    args = {{{", ".join([f'"{p}": {p}' for p in properties.keys()])}}}
    return await call_tool("{endpoint}", "{tool_name}", args)
'''
    
    # Execute the function definition
    namespace = {"call_tool": call_tool}
    exec(func_code, namespace)
    
    return namespace[tool_name]

# Dynamically register all tools from config
for tool_config in config["tools"]:
    tool_func = create_dynamic_tool(tool_config)
    mcp.tool()(tool_func)
    print(f"✅ Registered tool: {tool_config['name']}")

if __name__ == "__main__":
    print(f"🚀 Starting MCP Gateway with {len(config['tools'])} tools...")
    mcp.run(transport="sse", host="0.0.0.0", port=8001)