#!/usr/bin/env python3
"""
Test what FastMCP is actually seeing from our generated tools
"""

import subprocess
import sys
import json

def test_tool_introspection():
    """Test what the MCP server actually returns for tool metadata"""
    
    print("🔍 Testing Tool Introspection")
    print("============================")
    
    commands = [
        '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "introspect-test", "version": "1.0"}}}',
        '{"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}',
        '{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}'
    ]
    
    try:
        process = subprocess.Popen(
            [sys.executable, "mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        input_data = "\n".join(commands) + "\n"
        stdout, stderr = process.communicate(input=input_data, timeout=10)
        
        print("Analyzing tool metadata from MCP server...")
        
        for line in stdout.strip().split('\n'):
            if line.strip():
                try:
                    response = json.loads(line)
                    
                    if "result" in response and "tools" in response["result"]:
                        tools = response["result"]["tools"]
                        print(f"\n📋 Found {len(tools)} tools:")
                        
                        for tool in tools:
                            print(f"\n🔧 Tool: {tool['name']}")
                            print(f"   Description: {tool.get('description', 'No description')}")
                            
                            input_schema = tool.get('inputSchema', {})
                            if input_schema:
                                print(f"   Input Schema: {json.dumps(input_schema, indent=4)}")
                                
                                properties = input_schema.get('properties', {})
                                if properties:
                                    print(f"   Parameters:")
                                    for param_name, param_def in properties.items():
                                        param_desc = param_def.get('description', 'No description')
                                        param_type = param_def.get('type', 'unknown')
                                        param_default = param_def.get('default', 'No default')
                                        print(f"      - {param_name} ({param_type}): {param_desc}")
                                        if param_default != 'No default':
                                            print(f"        Default: {param_default}")
                                
                                required = input_schema.get('required', [])
                                if required:
                                    print(f"   Required: {required}")
                            else:
                                print(f"   ❌ No input schema found!")
                        
                        return True
                        
                except json.JSONDecodeError:
                    continue
        
        print("❌ No tools found in server response")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_tool_introspection()
    
    if success:
        print("\n🎯 Analysis complete!")
        print("Check if the input schema contains parameter descriptions.")
        print("If not, FastMCP isn't parsing our docstring properly.")
    else:
        print("\n💡 Server might not be working correctly.")
        print("Check logs/app.log for errors.")
        