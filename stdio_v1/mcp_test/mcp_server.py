#!/usr/bin/env python3
# mcp_server.py - Enhanced MCP Server with Dynamic Tool Loading
from fastmcp import FastMCP
from tool import register_all_tools
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Create MCP server
    mcp = FastMCP("GenBridge MCP Server")
    
    # Register all tools from tool.py
    tool_count = register_all_tools(mcp)
    logger.info(f"✅ Registered {tool_count} tools from tool.yml")
    
    if tool_count == 0:
        logger.warning("⚠️ No tools registered - check tool.yml configuration")
    
    # Run with stdio transport
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()