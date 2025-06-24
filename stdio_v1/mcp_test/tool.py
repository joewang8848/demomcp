# tool.py - Dynamic Tool Management for stdio MCP Server
import yaml
import logging
import importlib.util
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import inspect

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
        
        # Create unique module name to avoid conflicts
        module_name = f"tool_module_{app_file.stem}_{abs(hash(str(app_file)))}"
        
        # Create module spec and load module
        spec = importlib.util.spec_from_file_location(module_name, app_file)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load module spec from {app_path}")
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        return module
    except Exception as e:
        logger.error(f"Failed to load tool module from {app_path}: {e}")
        raise

class ToolWrapper:
    """Wrapper class to hold tool information and execute tool functions"""
    
    def __init__(self, tool_config: Dict[str, Any]):
        self.name = tool_config["name"]
        self.description = tool_config["description"]
        self.app_path = tool_config["app_path"]
        self.function_name = tool_config.get("function_name", self.name)
        self.schema = tool_config.get("input_schema", {})
        self.module = None
        
        # Load the module immediately
        try:
            self.module = load_tool_module(self.app_path)
            logger.info(f"✅ Loaded module for tool: {self.name}")
        except Exception as e:
            logger.error(f"❌ Failed to load module for tool {self.name}: {e}")
            raise
    
    async def execute(self, **kwargs) -> str:
        """Execute the tool function with given arguments"""
        try:
            if self.module is None:
                return f"Error: Module not loaded for tool {self.name}"
            
            if not hasattr(self.module, self.function_name):
                return f"Error: Function '{self.function_name}' not found in {self.app_path}"
            
            tool_function = getattr(self.module, self.function_name)
            
            if not callable(tool_function):
                return f"Error: '{self.function_name}' is not callable"
            
            # Execute function (handle both sync and async)
            if inspect.iscoroutinefunction(tool_function):
                result = await tool_function(**kwargs)
            else:
                result = tool_function(**kwargs)
                
            return str(result)
            
        except Exception as e:
            logger.error(f"Error executing tool {self.name}: {e}")
            return f"Error executing {self.name}: {str(e)}"

# Global registry of tool wrappers
_tool_registry = {}

def register_all_tools(mcp) -> int:
    """Register all tools with the MCP server"""
    global _tool_registry
    
    tools = load_tool_config()
    count = 0
    
    for tool_config in tools:
        try:
            # Validate required fields
            if "app_path" not in tool_config:
                logger.error(f"Tool {tool_config.get('name', 'unknown')} missing app_path")
                continue
            
            # Create tool wrapper
            tool_wrapper = ToolWrapper(tool_config)
            _tool_registry[tool_wrapper.name] = tool_wrapper
            
            # Create the actual tool function for FastMCP
            def make_tool_function(wrapper):
                # Build the function signature dynamically
                properties = wrapper.schema.get("properties", {})
                required = wrapper.schema.get("required", [])
                
                # Create parameter list
                params = []
                for prop_name, prop_def in properties.items():
                    if prop_name in required:
                        params.append(f"{prop_name}: str")
                    else:
                        default = prop_def.get("default", '""')
                        if isinstance(default, str):
                            default = f'"{default}"'
                        params.append(f"{prop_name}: str = {default}")
                
                # Create function dynamically
                param_str = ", ".join(params)
                param_names = list(properties.keys())
                
                async def tool_function(**kwargs) -> str:
                    # Filter kwargs to only include expected parameters
                    filtered_kwargs = {k: v for k, v in kwargs.items() if k in param_names}
                    return await wrapper.execute(**filtered_kwargs)
                
                # Set function metadata
                tool_function.__name__ = wrapper.name
                tool_function.__doc__ = wrapper.description
                
                # Create proper annotations
                annotations = {}
                for prop_name in properties.keys():
                    annotations[prop_name] = str
                annotations['return'] = str
                tool_function.__annotations__ = annotations
                
                return tool_function
            
            # Register with MCP
            tool_func = make_tool_function(tool_wrapper)
            mcp.tool()(tool_func)
            
            logger.info(f"✅ Registered tool: {tool_wrapper.name} -> {tool_wrapper.app_path}")
            count += 1
            
        except Exception as e:
            logger.error(f"❌ Failed to register {tool_config.get('name', 'unknown')}: {e}")
    
    return count