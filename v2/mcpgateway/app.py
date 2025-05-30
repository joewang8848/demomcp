# app.py - MCP Gateway Only
import yaml
from fastmcp import FastMCP
from utils.logger import setup_logging
from tool import register_all_tools

def load_gateway_config(path: str = "gateway.yml") -> dict:
    """Load gateway configuration"""
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        # Default gateway config
        return {
            "server": {
                "host": "0.0.0.0",
                "port": 8001,
                "transport": "sse"
            },
            "gateway": {
                "name": "MCP Gateway",
                "version": "2.0.0"
            }
        }

def main():
    # Setup logging
    setup_logging()
    
    # Load gateway configuration
    config = load_gateway_config()
    
    # Create MCP server
    gateway_name = config["gateway"]["name"]
    mcp = FastMCP(gateway_name)
    
    # Register all tools from tool.py
    tool_count = register_all_tools(mcp)
    print(f"✅ Registered {tool_count} tools")
    
    # Start gateway
    server_config = config["server"]
    print(f"🚀 Starting {gateway_name} on {server_config['host']}:{server_config['port']}")
    
    mcp.run(
        transport=server_config["transport"],
        host=server_config["host"], 
        port=server_config["port"]
    )

if __name__ == "__main__":
    main()