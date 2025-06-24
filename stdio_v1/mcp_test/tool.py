# tool.py - Dynamic Tool Management for stdio MCP Server
import yaml
import logging
import importlib.util
import sys
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def load_tool_config():
    """Load tool configuration from tool.yml"""
    try:
        with open("tool.yml", 'r') as f:
            config = yaml.safe_load(f)
            tools = config.get("tools", [])
            logger.info(f"Loaded {len(tools)} tools from tool.yml")
            return tools
    except FileNotFoundError:
        logger.error("tool.yml file not found")
        return []
    except Exception as e:
        logger.error(f"Failed to load tool config: {e}")
        return []

def load_tool_module(app_path: str):
    """Dynamically import a tool module from app.py path"""
    try:
        app_file = Path(app_path)
        if not app_file.exists():
            raise FileNotFoundError(f"Tool app file not found: {app_path}")
        
        # Create module spec and load module
        spec = importlib.util.spec_from_file_location("tool_module", app_file)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load module spec from {app_path}")
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        return module
    except Exception as e:
        logger.error(f"Failed to load tool module from {app_path}: {e}")
        raise

async def execute_tool_from_module(app_path: str, function_name: str, args: Dict[str, Any]) -> str:
    """Execute a tool function from a dynamically loaded module"""
    try:
        module = load_tool_module(app_path)
        
        if not hasattr(module, function_name):
            raise AttributeError(f"Function '{function_name}' not found in {app_path}")
        
        tool_function = getattr(module, function_name)
        
        # Call the function with arguments
        if callable(tool_function):
            # Check if it's async
            if hasattr(tool_function, '__call__'):
                import inspect
                if inspect.iscoroutinefunction(tool_function):
                    result = await tool_function(**args)
                else:
                    result = tool_function(**args)
                return str(result)
            else:
                raise TypeError(f"'{function_name}' is not callable")
        else:
            raise TypeError(f"'{function_name}' is not a function")
            
    except Exception as e:
        logger.error(f"Error executing tool function {function_name} from {app_path}: {e}")
        return f"Error: {str(e)}"

def create_tool_function(tool_config: Dict[str, Any]):
    """Create a tool function dynamically from configuration"""
    name = tool_config["name"]
    description = tool_config["description"]
    app_path = tool_config["app_path"]
    function_name = tool_config.get("function_name", name)  # Default to tool name
    schema = tool_config.get("input_schema", {})
    
    # Build parameter signature dynamically
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
    
    # Create the function code
    func_code = f'''
async def {name}({", ".join(params)}) -> str:
    """{description}"""
    args = {{{", ".join([f'"{p}": {p}' for p in properties.keys()])}}}
    return await execute_tool_from_module("{app_path}", "{function_name}", args)
'''
    
    # Execute the function code and return the function
    namespace = {"execute_tool_from_module": execute_tool_from_module}
    exec(func_code, namespace)
    return namespace[name]

def register_all_tools(mcp) -> int:
    """Register all tools with the MCP server"""
    tools = load_tool_config()
    count = 0
    
    for tool_config in tools:
        try:
            # Validate required fields
            if "app_path" not in tool_config:
                logger.error(f"Tool {tool_config.get('name', 'unknown')} missing app_path")
                continue
                
            tool_func = create_tool_function(tool_config)
            mcp.tool()(tool_func)
            logger.info(f"✅ Registered tool: {tool_config['name']} -> {tool_config['app_path']}")
            count += 1
        except Exception as e:
            logger.error(f"❌ Failed to register {tool_config.get('name', 'unknown')}: {e}")
    
    return count