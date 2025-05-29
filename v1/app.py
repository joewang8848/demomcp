import os
import logging
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server.log'),
        logging.StreamHandler()  # This will print to console
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
app = FastAPI()

# Load tool manifest
try:
    with open("weather_tool_manifest.json") as f:
        manifest = json.load(f)
    logger.info(f"Loaded manifest: {manifest}")
except Exception as e:
    logger.error(f"Failed to load manifest: {e}")
    manifest = {}

# MCP-specific models (not standard JSON-RPC)
class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: int | str
    method: str
    params: dict | None = None

class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: int | str
    result: dict | None = None

class MCPErrorResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: int | str
    error: dict

# Helper: get OpenWeather API key
def get_api_key() -> str:
    key = os.getenv("OPENWEATHER_API_KEY")
    if not key:
        logger.error("OPENWEATHER_API_KEY environment variable not set")
        raise HTTPException(status_code=500, detail="OPENWEATHER_API_KEY not set")
    logger.info("OpenWeather API key loaded successfully")
    return key

# Helper: fetch raw weather data
async def fetch_current_weather(location: str, units: str = "metric") -> dict:
    params = {"q": location, "units": units, "appid": get_api_key()}
    logger.info(f"Fetching weather data for location: {location}, units: {units}")
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.openweathermap.org/data/2.5/weather", params=params
            )
            resp.raise_for_status()
            data = resp.json()
            logger.info(f"Weather API response: {json.dumps(data, indent=2)}")
            return data
    except Exception as e:
        logger.error(f"Weather API request failed: {str(e)}")
        raise

# MCP endpoint
@app.post("/mcp")
async def mcp_endpoint(request: Request):
    timestamp = datetime.now().isoformat()
    logger.info(f"=== MCP REQUEST START [{timestamp}] ===")
    
    try:
        # Log raw request
        body = await request.json()
        logger.info(f"Raw request body: {json.dumps(body, indent=2)}")
        
        # Log request headers
        headers = dict(request.headers)
        logger.info(f"Request headers: {json.dumps(headers, indent=2)}")
        
        req = MCPRequest(**body)
        logger.info(f"Parsed MCP request - Method: {req.method}, ID: {req.id}, Params: {req.params}")
        
        response_data = None
        
        # Only JSON-RPC 2.0
        if req.jsonrpc != "2.0":
            logger.warning(f"Invalid JSON-RPC version: {req.jsonrpc}")
            response_data = MCPErrorResponse(
                id=req.id,
                error={"code": -32600, "message": "Invalid Request - only JSON-RPC 2.0 supported"}
            ).dict()

        # Handle initialize method
        elif req.method == "initialize":
            logger.info("Processing initialize request")
            response_data = MCPResponse(
                id=req.id,
                result={
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "weather-server",
                        "version": "1.0.0"
                    }
                }
            ).dict()

        # Handle tools/list method
        elif req.method == "tools/list":
            logger.info("Processing tools/list request")
            tool_def = {
                "name": manifest.get("name", "get_current_weather"),
                "description": manifest.get("description", "Get current weather for a location"),
                "inputSchema": manifest.get("parameters", {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "City name"},
                        "units": {"type": "string", "enum": ["metric", "imperial"], "default": "metric"}
                    },
                    "required": ["location"]
                })
            }
            logger.info(f"Returning tool definition: {json.dumps(tool_def, indent=2)}")
            response_data = MCPResponse(
                id=req.id,
                result={"tools": [tool_def]}
            ).dict()

        # Handle tools/call method
        elif req.method == "tools/call":
            logger.info("Processing tools/call request")
            
            if not req.params:
                logger.error("Missing parameters in tools/call request")
                response_data = MCPErrorResponse(
                    id=req.id,
                    error={"code": -32602, "message": "Missing parameters"}
                ).dict()
            else:
                tool_name = req.params.get("name")
                arguments = req.params.get("arguments", {})
                logger.info(f"Tool call - Name: {tool_name}, Arguments: {arguments}")
                
                if tool_name != manifest.get("name", "get_current_weather"):
                    logger.error(f"Unknown tool requested: {tool_name}")
                    response_data = MCPErrorResponse(
                        id=req.id,
                        error={"code": -32601, "message": f"Tool '{tool_name}' not found"}
                    ).dict()
                else:
                    location = arguments.get("location")
                    units = arguments.get("units", "metric")
                    
                    if not location:
                        logger.error("Missing required parameter: location")
                        response_data = MCPErrorResponse(
                            id=req.id,
                            error={"code": -32602, "message": "Missing required parameter: location"}
                        ).dict()
                    else:
                        try:
                            logger.info(f"Calling weather API for location: {location}")
                            data = await fetch_current_weather(location, units)
                            text = f"Current weather in {location}: Temperature: {data['main']['temp']}°, Conditions: {data['weather'][0]['description']}"
                            logger.info(f"Generated weather response: {text}")
                            
                            response_data = MCPResponse(
                                id=req.id,
                                result={
                                    "content": [{"type": "text", "text": text}],
                                    "isError": False
                                }
                            ).dict()
                        except Exception as e:
                            logger.error(f"Weather API call failed: {str(e)}")
                            response_data = MCPErrorResponse(
                                id=req.id,
                                error={"code": -32603, "message": f"Weather API error: {str(e)}"}
                            ).dict()

        # Method not found
        else:
            logger.warning(f"Unknown method requested: {req.method}")
            response_data = MCPErrorResponse(
                id=req.id,
                error={"code": -32601, "message": f"Method '{req.method}' not found"}
            ).dict()

        # Log the response
        logger.info(f"MCP Response: {json.dumps(response_data, indent=2)}")
        logger.info(f"=== MCP REQUEST END [{timestamp}] ===")
        
        return response_data

    except Exception as e:
        logger.error(f"Unexpected error processing MCP request: {str(e)}", exc_info=True)
        error_response = MCPErrorResponse(
            id=getattr(req, 'id', 0) if 'req' in locals() else 0,
            error={"code": -32700, "message": f"Parse error: {str(e)}"}
        ).dict()
        logger.info(f"Error response: {json.dumps(error_response, indent=2)}")
        logger.info(f"=== MCP REQUEST END (ERROR) [{timestamp}] ===")
        return error_response

# Health check with logging
@app.get("/ping")
async def ping() -> dict:
    logger.info("Health check ping received")
    response = {"pong": True, "timestamp": datetime.now().isoformat()}
    logger.info(f"Health check response: {response}")
    return response

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("=== MCP Weather Server Starting ===")
    logger.info(f"Server started at {datetime.now().isoformat()}")
    logger.info(f"Manifest loaded: {bool(manifest)}")
    logger.info(f"OpenWeather API Key configured: {bool(os.getenv('OPENWEATHER_API_KEY'))}")
    logger.info("=== Server Ready ===")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("=== MCP Weather Server Shutting Down ===")
    logger.info(f"Server stopped at {datetime.now().isoformat()}")
    logger.info("=== Server Stopped ===")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server with uvicorn")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")