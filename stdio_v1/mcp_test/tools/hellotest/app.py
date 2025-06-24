# tools/hellotest/app.py - Hello Test Tool
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from user import User
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
    
    #return f"{message}, {name}! 👋 Welcome to the MCP server!"
    user = User(name)
    return user.hello(message)


