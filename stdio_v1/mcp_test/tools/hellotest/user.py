# tools/hellotest/user.py - User Class
"""
User class for handling greetings
"""

class User:
    """
    User class that handles greeting functionality
    """
    
    def __init__(self, name: str):
        """
        Initialize User with a name
        
        Args:
            name: Name of the user
        """
        self.name = name
    
    def hello(self, message: str = "Hello") -> str:
        """
        Generate a greeting message for this user
        
        Args:
            message: Custom greeting message (default: "Hello")
        
        Returns:
            Formatted greeting string
        """
        if not self.name:
            return "Error: User name is required"
        
        return f"{message}, {self.name}! 👋 Welcome to the MCP server!"
    
    def __str__(self):
        """String representation of the user"""
        return f"User(name='{self.name}')"
    
    def __repr__(self):
        """Detailed representation of the user"""
        return f"User(name='{self.name}')"