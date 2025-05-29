# app.py - Weather Tool (Minimal)
import os
import httpx
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any, Union

app = FastAPI()

class ToolRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    request_id: Union[int, str]

@app.post("/v1/get_current_weather")
async def get_weather(request: ToolRequest):
    try:
        location = request.arguments.get("location")
        units = request.arguments.get("units", "metric")
        
        if not location:
            return {"content": [{"type": "text", "text": "Missing location"}], "isError": True}
        
        # Get weather
        api_key = os.getenv("OPENWEATHER_API_KEY")
        url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&units={units}&appid={api_key}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
            
            if response.status_code != 200:
                return {"content": [{"type": "text", "text": f"Error: {data.get('message', 'API error')}"}], "isError": True}
            
            temp = data['main']['temp']
            desc = data['weather'][0]['description']
            temp_unit = "°C" if units == "metric" else "°F"
            
            text = f"Weather in {location}: {temp}{temp_unit}, {desc}"
            return {"content": [{"type": "text", "text": text}], "isError": False}
            
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error: {str(e)}"}], "isError": True}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9001)