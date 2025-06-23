#!/bin/bash
set -e

echo "🚀 Setting up MCP Server"
echo "========================"

# Check for Python - try python3 first, then python
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo "✅ Found python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo "✅ Found python"
else
    echo "❌ Python is required but not found (tried python3 and python)"
    exit 1
fi

# Verify Python version (should be 3.8+)
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
if [[ ! $PYTHON_VERSION =~ ^3\.[8-9]|^3\.[1-9][0-9] ]]; then
    echo "⚠️  Warning: Python 3.8+ recommended (found $PYTHON_VERSION)"
fi

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    $PYTHON_CMD -m venv .venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
echo "🔧 Installing dependencies..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Test the server:"
echo "   source .venv/bin/activate"
echo "   python mcp_server.py"
echo ""
echo "2. Copy this JSON to your Claude Desktop config:"
echo ""
echo "{"
echo "  \"mcpServers\": {"
echo "    \"mcp-test\": {"
echo "      \"command\": \"$(pwd)/.venv/bin/python\","
echo "      \"args\": [\"$(pwd)/mcp_server.py\"],"
echo "      \"cwd\": \"$(pwd)\","
echo "      \"autoApprove\": [],"
echo "      \"disabled\": false,"
echo "      \"timeout\": 60,"
echo "      \"env\": {"
echo "        \"OPEN_API_KEY\": \"ABC\""
echo "      }"
echo "    }"
echo "  }"
echo "}"