# demomcp

## Architecture Diagrams

### V1 Architecture
```mermaid
graph LR
    User[User] --> Client
    
    subgraph Client
        AI[AI Assistants]
        Web[Web Interface]
    end
    
    Client --> WeatherTool[All-in-One Weather Tool]
    
    style Client fill:#f9f,stroke:#333,stroke-width:2px
    style WeatherTool fill:#bbf,stroke:#333,stroke-width:2px
    style User fill:#f9f,stroke:#333,stroke-width:2px
    style AI fill:#f9f,stroke:#333,stroke-width:2px
    style Web fill:#f9f,stroke:#333,stroke-width:2px
```

### V2 Architecture
```mermaid
graph LR
    User[User] --> Client
    
    subgraph Client
        AI[AI Assistants]
        Web[Web Interface]
    end
    
    Client --> MCPGateway[MCP Gateway]
    Dispatcher -.-> Tools
    
    subgraph Tools
        WeatherTool[Weather Tool]
    end
    
    subgraph External Services
        API[Weather API]
    end
    
    WeatherTool --> API
    
    subgraph MCP Gateway Components
        MCPGateway --> Config[Configuration]
        MCPGateway --> Logger[Logger]
        MCPGateway --> Models[MCP Models]
        MCPGateway --> Dispatcher[Dispatcher Service]
    end
      style Client fill:#f9f,stroke:#333,stroke-width:2px
    style User fill:#f9f,stroke:#333,stroke-width:2px
    style AI fill:#f9f,stroke:#333,stroke-width:2px
    style Web fill:#f9f,stroke:#333,stroke-width:2px
    style MCPGateway fill:#bbf,stroke:#333,stroke-width:2px
    style Dispatcher fill:#fbb,stroke:#333,stroke-width:2px
    style WeatherTool fill:#bbf,stroke:#333,stroke-width:2px
    style API fill:#ddf,stroke:#333,stroke-width:2px
    style Config fill:#fbb,stroke:#333,stroke-width:2px
    style Logger fill:#fbb,stroke:#333,stroke-width:2px
    style Models fill:#fbb,stroke:#333,stroke-width:2px
    style Tools fill:#bbf,stroke:#333,stroke-width:2px
    style External Services fill:#ddf,stroke:#333,stroke-width:2px
    style MCP Gateway Components fill:#bbf,stroke:#333,stroke-width:2px
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