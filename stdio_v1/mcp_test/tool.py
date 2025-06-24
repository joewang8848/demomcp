# tool.py - Simple Tool Management (Standard Registration Only)
import yaml
import logging
import importlib.util
import inspect
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

def load_tool_config():
    """Load tool configuration from tool.yml"""
    try:
        with open("tool.yml", 'r') as f:
            tools = yaml.safe_load(f).get("tools", [])
            logger.info(f"Loaded {len(tools)} tools from tool.yml")
            return tools
    except Exception as e:
        logger.error(f"Failed to load tool config: {e}")
        return []

def load_tool_module(app_path: str, tool_name: str):
    """Load a tool module dynamically"""
    app_file = Path(app_path)
    if not app_file.exists():
        raise FileNotFoundError(f"Tool app file not found: {app_path}")
    
    module_name = f"tool_{tool_name}_{abs(hash(str(app_file)))}"
    spec = importlib.util.spec_from_file_location(module_name, app_file)
    
    if not spec or not spec.loader:
        raise ImportError(f"Could not load module spec from {app_path}")
    
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    logger.info(f"Loaded module for tool: {tool_name}")
    return module

def create_tool_function(tool_config: Dict[str, Any], mcp) -> bool:
    """Create and register a dynamic tool function"""
    name = tool_config["name"]
    base_description = tool_config["description"]
    app_path = tool_config["app_path"]
    function_name = tool_config.get("function_name", name)
    schema = tool_config.get("input_schema", {})
    
    try:
        # Load module and get function
        module = load_tool_module(app_path, name)
        
        if not hasattr(module, function_name):
            available = [attr for attr in dir(module) if callable(getattr(module, attr)) and not attr.startswith('_')]
            logger.error(f"Function '{function_name}' not found. Available: {available}")
            return False
        
        original_function = getattr(module, function_name)
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        
        # Build comprehensive description with parameter information
        description_parts = [base_description]
        
        if properties:
            description_parts.append("\nParameters:")
            for prop_name, prop_def in properties.items():
                param_desc = prop_def.get("description", f"{prop_name} parameter")
                is_required = prop_name in required
                default_value = prop_def.get("default")
                
                param_info = f"• {prop_name}: {param_desc}"
                if is_required:
                    param_info += " (required)"
                elif default_value is not None:
                    param_info += f" (default: '{default_value}')"
                else:
                    param_info += " (optional)"
                    
                description_parts.append(param_info)
        
        # Combine into comprehensive description
        comprehensive_description = "\n".join(description_parts)
        
        # Build function signature
        params = []
        param_names = list(properties.keys())
        
        for prop_name, prop_def in properties.items():
            if prop_name in required:
                params.append(f"{prop_name}: str")
            else:
                default_value = prop_def.get("default", "")
                if isinstance(default_value, str):
                    params.append(f'{prop_name}: str = "{default_value}"')
                else:
                    params.append(f"{prop_name}: str = '{default_value}'")
        
        param_signature = ", ".join(params)
        
        # Create function with comprehensive description
        function_code = f'''
async def {name}({param_signature}) -> str:
    """{comprehensive_description}"""
    try:
        args = {{{", ".join([f'"{p}": {p}' for p in param_names])}}}
        
        # Validate required parameters
        for req in {required}:
            if not args.get(req):
                return f"Error: Required parameter '{{req}}' is missing"
        
        # Call original function
        if inspect.iscoroutinefunction(original_function):
            result = await original_function(**args)
        else:
            result = original_function(**args)
        
        logger.info(f"Tool {name} executed successfully")
        return str(result)
        
    except Exception as e:
        logger.error(f"Tool {name} error: {{e}}")
        return f"Error: {{str(e)}}"
'''
        
        # Execute and register with standard method only
        namespace = {
            'original_function': original_function,
            'required': required,
            'param_names': param_names,
            'logger': logger,
            'inspect': inspect
        }
        
        exec(function_code, namespace)
        tool_function = namespace[name]
        tool_function.__name__ = name
        
        # Standard registration - simple and reliable
        mcp.tool()(tool_function)
        
        logger.info(f"Registered tool: {name}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create tool {name}: {e}")
        return False

def register_all_tools(mcp) -> int:
    """Register all tools from configuration"""
    logger.info("Starting tool registration")
    
    tools = load_tool_config()
    if not tools:
        return 0
    
    count = 0
    required_fields = ["name", "description", "app_path"]
    
    for tool_config in tools:
        name = tool_config.get("name", "unknown")
        
        # Validate required fields
        missing = [field for field in required_fields if not tool_config.get(field)]
        if missing:
            logger.error(f"Tool {name} missing fields: {missing}")
            continue
        
        if create_tool_function(tool_config, mcp):
            count += 1
    
    logger.info(f"Registration complete: {count}/{len(tools)} tools")
    return count