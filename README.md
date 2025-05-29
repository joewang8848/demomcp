# demomcp

## Architecture Diagrams

### V1 Architecture
```mermaid
graph LR
    Client[Client] --> WeatherTool[Weather Tool]
    WeatherTool --> API[Weather API]
    
    style Client fill:#f9f,stroke:#333,stroke-width:2px
    style WeatherTool fill:#bbf,stroke:#333,stroke-width:2px
    style API fill:#ddf,stroke:#333,stroke-width:2px
```

### V2 Architecture
```mermaid
graph LR
    Client[Client] --> MCPGateway[MCP Gateway]
    MCPGateway --> Dispatcher[Dispatcher Service]
    Dispatcher --> WeatherTool[Weather Tool]
    WeatherTool --> API[Weather API]
    
    subgraph MCP Gateway Components
        MCPGateway --> Config[Configuration]
        MCPGateway --> Logger[Logger]
        MCPGateway --> Models[MCP Models]
    end
    
    style Client fill:#f9f,stroke:#333,stroke-width:2px
    style MCPGateway fill:#bbf,stroke:#333,stroke-width:2px
    style Dispatcher fill:#bfb,stroke:#333,stroke-width:2px
    style WeatherTool fill:#bbf,stroke:#333,stroke-width:2px
    style API fill:#ddf,stroke:#333,stroke-width:2px
    style Config fill:#fbb,stroke:#333,stroke-width:2px
    style Logger fill:#fbb,stroke:#333,stroke-width:2px
    style Models fill:#fbb,stroke:#333,stroke-width:2px
```

### Key Differences

1. **V1 (Simple Architecture)**
   - Direct client-to-tool communication
   - Single weather tool component
   - Basic functionality without middleware

2. **V2 (MCP Architecture)**
   - Introduces MCP Gateway as middleware
   - Dispatcher service for tool management
   - Modular components (Config, Logger, Models)
   - Enhanced flexibility and scalability
   - Supports multiple tools through common interface