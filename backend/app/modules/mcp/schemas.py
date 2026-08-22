# pyrefly: ignore [missing-import]
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class MCPToolInputSchema(BaseModel):
    type: str = "object"
    properties: Dict[str, Any]
    required: Optional[List[str]] = []

class MCPToolDefinition(BaseModel):
    name: str
    description: str
    inputSchema: MCPToolInputSchema

class MCPCallToolRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]

class MCPCallToolResponse(BaseModel):
    status: str
    result: Dict[str, Any]
