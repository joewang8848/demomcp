@echo off
echo 🚀 Setting up MCP Server
echo ========================

REM Check for Python - try python first, then python3
set PYTHON_CMD=
python --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=python
    echo ✅ Found python
) else (
    python3 --version >nul 2>&1
    if %errorlevel% == 0 (
        set PYTHON_CMD=python3
        echo ✅ Found python3
    ) else (
        echo ❌ Python is required but not found (tried python and python3)
        pause
        exit /b 1
    )
)

REM Create virtual environment
if not exist ".venv" (
    echo 📦 Creating virtual environment...
    %PYTHON_CMD% -m venv .venv
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment and install dependencies
echo 🔧 Installing dependencies...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Get current directory with escaped backslashes for JSON
set "CURRENT_DIR=%CD%"
set "ESCAPED_DIR=%CURRENT_DIR:\=\\%"

echo.
echo ✅ Setup complete!
echo.
echo 🎯 Next steps:
echo 1. Test the server:
echo    .venv\Scripts\activate.bat
echo    python mcp_server.py
echo.
echo 2. Copy this JSON to your AI Assistant config:
echo.
echo {
echo   "mcpServers": {
echo     "mcp-test": {
echo       "command": "%ESCAPED_DIR%\\.venv\\Scripts\\python.exe",
echo       "args": ["mcp_server.py"],
echo       "cwd": "%ESCAPED_DIR%",
echo       "autoApprove": [],
echo       "disabled": false,
echo       "timeout": 60,
echo       "env": {
echo         "OPEN_API_KEY": "ABC"
echo       }
echo     }
echo   }
echo }
echo.
pause