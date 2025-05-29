#!/usr/bin/env bash

echo "🧪 SQL Generator Tool Test"
echo "=========================="

# Test 1: Health check
echo "1. Testing SQL Generator health..."
curl -s http://localhost:9002/health | jq .

# Test 2: Direct SQL Generator Tool
echo -e "\n2. Testing SQL generator directly..."
curl -s -X POST http://localhost:9002/v1/generate_sql_files \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "generate_sql_files",
    "arguments": {
      "streamid": "user_analytics_001",
      "sql_content": "SELECT user_id, count(*) as login_count\nFROM user_sessions\nWHERE created_at >= CURRENT_DATE - INTERVAL 30 DAY\nGROUP BY user_id\nORDER BY login_count DESC;"
    },
    "request_id": 1
  }' | jq .

# Test 3: End-to-End via MCP Gateway
echo -e "\n3. Testing via MCP Gateway..."
curl -s -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "generate_sql_files",
      "arguments": {
        "streamid": "sales_report_q1",
        "sql_content": "SELECT \n  product_category,\n  SUM(revenue) as total_revenue,\n  COUNT(DISTINCT customer_id) as unique_customers\nFROM sales_transactions\nWHERE quarter = 1 AND year = 2025\nGROUP BY product_category;"
      }
    }
  }' | jq .

echo -e "\n✅ SQL Generator tests completed!"