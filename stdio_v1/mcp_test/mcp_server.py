#!/usr/bin/env python3
# mcp_server.py - Enhanced MCP Server with Dynamic Tool Loading
from fastmcp import FastMCP
from tool import register_all_tools
import logging
import os
from pathlib import Path

def setup_logging():
    """Setup file logging to logs/app.log"""
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure logging to file
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(logs_dir / "app.log"),
            logging.StreamHandler()  # Keep console output for important messages
        ]
    )

logger = logging.getLogger(__name__)

def main():
    # Setup file logging first
    setup_logging()
    
    logger.info("🚀 Starting Enhanced MCP Server with Dynamic Tool Loading")
    
    # Create MCP server
    mcp = FastMCP("Enhanced MCP Server")
    
    # Register all tools from tool.py
    tool_count = register_all_tools(mcp)
    logger.info(f"✅ Registered {tool_count} tools from tool.yml")
    
    if tool_count == 0:
        logger.warning("⚠️ No tools registered - check tool.yml configuration")
    
    # Log that we're starting with stdio transport
    logger.info("🔗 Starting MCP server with stdio transport")
    
    # Run with stdio transport
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()