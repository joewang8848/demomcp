#!/usr/bin/env bash

echo "🧪 Simple End-to-End Test"
echo "========================"

# Test 1: Health checks
echo "1. Testing health endpoints..."
curl -s http://localhost:8001/health | jq .
curl -s http://localhost:9001/health | jq .

# Test 2: MCP Tools List
echo -e "\n2. Testing MCP tools list..."
curl -s -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | jq .

# Test 3: Direct Weather Tool
echo -e "\n3. Testing weather tool directly..."
curl -s -X POST http://localhost:9001/v1/get_current_weather \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "get_current_weather",
    "arguments": {"location": "London"},
    "request_id": 1
  }' | jq .

# Test 4: End-to-End via MCP Gateway
echo -e "\n4. Testing end-to-end via MCP Gateway..."
curl -s -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "get_current_weather",
      "arguments": {"location": "Paris", "units": "metric"}
    }
  }' | jq .

echo -e "\n✅ Tests completed!"