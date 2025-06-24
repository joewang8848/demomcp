#!/usr/bin/env python3
# mcp_server.py - Generic MCP Server
from fastmcp import FastMCP
from tool import register_all_tools
import logging
import sys
from pathlib import Path

def setup_logging():
    """Setup file and console logging"""
    Path("logs").mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("logs/app.log", encoding='utf-8'),
            logging.StreamHandler(sys.stderr)
        ]
    )

def main():
    """Start the MCP server with dynamic tool loading"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting GenBridge MCP Server")
        
        mcp = FastMCP("GenBridge MCP Server")
        tool_count = register_all_tools(mcp)
        
        logger.info(f"Registered {tool_count} tools - starting stdio transport")
        
        if tool_count == 0:
            logger.warning("No tools registered - check tool.yml configuration")
        
        mcp.run(transport="stdio")
        
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()