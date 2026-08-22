# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from app.core.security import get_current_user, TokenPayload, require_role
from app.modules.mcp.schemas import MCPCallToolRequest, MCPCallToolResponse
from app.modules.mcp.simrs_server import simrs_mcp_server

router = APIRouter(prefix="/mcp", tags=["Model Context Protocol (MCP)"])

@router.get("/tools")
def list_mcp_tools(current_user: TokenPayload = Depends(require_role(["doctor", "admin"]))):
    """Exposes registered Model Context Protocol (MCP) Tools declarations."""
    return {
        "protocol_version": simrs_mcp_server.PROTOCOL_VERSION,
        "server_name": simrs_mcp_server.SERVER_NAME,
        "tools": simrs_mcp_server.list_tools()
    }

@router.post("/call", response_model=MCPCallToolResponse)
def execute_mcp_tool_call(
    request: MCPCallToolRequest,
    current_user: TokenPayload = Depends(require_role(["doctor", "admin"]))
):
    """Executes Model Context Protocol (MCP) tool call over JSON-RPC interface."""
    res = simrs_mcp_server.call_tool(request.tool_name, request.arguments)
    status_str = res.get("status", "success")
    return MCPCallToolResponse(status=status_str, result=res)
