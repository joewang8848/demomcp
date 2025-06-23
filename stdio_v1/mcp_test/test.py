#!/usr/bin/env python3
"""
Simple test script for the MCP server
Note: Make sure to activate .venv before running this test
"""

import json
import subprocess
import sys
import time
import os

def test_mcp_server():
    """Test the MCP server with basic commands"""
    print("🧪 Testing MCP Server")
    print("=====================")
    
    # Check if mcp_server.py exists
    if not os.path.exists("mcp_server.py"):
        print("❌ mcp_server.py not found in current directory")
        return False
    
    # Test commands
    commands = [
        {
            "jsonrpc": "2.0", 
            "id": 1, 
            "method": "initialize", 
            "params": {
                "protocolVersion": "2024-11-05", 
                "capabilities": {}, 
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        },
        {
            "jsonrpc": "2.0", 
            "id": 2, 
            "method": "tools/list", 
            "params": {}
        },
        {
            "jsonrpc": "2.0", 
            "id": 3, 
            "method": "tools/call", 
            "params": {
                "name": "test_mcp",
                "arguments": {"name": "Alice"}
            }
        }
    ]
    
    try:
        print("🚀 Starting MCP server...")
        
        # Start the MCP server
        process = subprocess.Popen(
            [sys.executable, "mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send commands
        input_data = "\n".join(json.dumps(cmd) for cmd in commands) + "\n"
        
        print("📤 Sending test commands...")
        stdout, stderr = process.communicate(input=input_data, timeout=10)
        
        print("📥 Server responses:")
        for line in stdout.strip().split('\n'):
            if line.strip():
                try:
                    response = json.loads(line)
                    if "result" in response:
                        if "tools" in response["result"]:
                            tools = response["result"]["tools"]
                            print(f"   ✅ Found {len(tools)} tools:")
                            for tool in tools:
                                print(f"      - {tool['name']}: {tool['description']}")
                        elif "content" in response["result"]:
                            content = response["result"]["content"][0]["text"]
                            print(f"   ✅ Tool response: {content}")
                        else:
                            print(f"   ✅ Initialize successful")
                    else:
                        print(f"   📄 Response: {response}")
                except json.JSONDecodeError:
                    print(f"   📄 Raw: {line}")
        
        if stderr:
            print("📋 Server logs:")
            for line in stderr.strip().split('\n'):
                if line.strip():
                    print(f"   {line}")
        
        print("✅ Test completed successfully!")
        return True
        
    except subprocess.TimeoutExpired:
        print("⏰ Test timed out")
        process.kill()
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_mcp_server()
    sys.exit(0 if success else 1)