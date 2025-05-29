# config.py - Configuration
import yaml
from pydantic import BaseModel
from typing import List, Dict, Any

class ToolConfig(BaseModel):
    name: str
    description: str
    endpoint: str
    input_schema: Dict[str, Any]

class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000

class Settings(BaseModel):
    rpc_path: str = "/mcp"
    server: ServerConfig = ServerConfig()
    tools: List[ToolConfig] = []

def load_config(path: str = "config.yaml") -> Settings:
    try:
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return Settings(**data)
    except:
        return Settings()

settings = load_config()