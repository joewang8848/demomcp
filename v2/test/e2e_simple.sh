#!/usr/bin/env bash

echo "🧪 Simple End-to-End Test (v2)"
echo "==============================="

# Test 1: Health check
echo "1. Testing MCP Gateway health..."
curl -s http://localhost:8001/health || echo "❌ Gateway health check failed"

# Test 2: Tool service health checks  
echo -e "\n2. Testing tool services health..."
curl -s http://localhost:9001/health | jq . || echo "❌ Weather tool not available"
curl -s http://localhost:9002/health | jq . || echo "❌ SQL Generator tool not available"

# Test 3: List available tools via FastMCP
echo -e "\n3. Testing FastMCP tools endpoint..."
curl -s http://localhost:8001/tools || echo "❌ Tools endpoint not available"

# Test 4: Direct Weather Tool
echo -e "\n4. Testing weather tool directly..."
curl -s -X POST http://localhost:9001/v1/get_current_weather \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "get_current_weather",
    "arguments": {"location": "London"},
    "request_id": 1
  }' | jq .

# Test 5: Direct SQL Generator Tool
echo -e "\n5. Testing SQL generator tool directly..."
curl -s -X POST http://localhost:9002/v1/generate_sql_files \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "generate_sql_files", 
    "arguments": {
      "streamid": "test_001",
      "sql_content": "SELECT * FROM users;"
    },
    "request_id": 1
  }' | jq .

echo -e "\n✅ Tests completed!"
echo "💡 Note: This tests direct tool calls. FastMCP uses SSE transport."
echo "💡 Use Claude Desktop or MCP client to test full FastMCP integration."