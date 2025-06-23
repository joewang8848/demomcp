#!/usr/bin/env python3
from fastmcp import FastMCP

mcp = FastMCP("MCP Server")

@mcp.tool()
async def test_mcp(name: str) -> str:
    # Description - used for ai assistant instruction
    """Name greeting test - enter your name to get a greeting"""
    # Core business logics
    return f"Hello {name}"

if __name__ == "__main__":
    mcp.run(transport="stdio")