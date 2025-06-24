# tools/hellotest/app.py - Hello Test Tool
"""
Simple hello greeting tool implementation
"""

def hello_function(name: str, message: str = "Hello") -> str:
    """
    Generate a greeting message
    
    Args:
        name: Name of the person to greet
        message: Custom greeting message (default: "Hello")
    
    Returns:
        Formatted greeting string
    """
    if not name:
        return "Error: Name is required"
    
    return f"{message}, {name}! 👋 Welcome to the MCP server!"

# You can add more functions here that can be called from tool.yml
def goodbye_function(name: str) -> str:
    """Say goodbye to someone"""
    return f"Goodbye, {name}! Thanks for using the MCP server! 👋"