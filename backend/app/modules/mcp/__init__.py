"""
MCP (Model Context Protocol) Module
Independent Modular Monolith domain managing MCP Servers, Client Bridges, and Standard JSON-RPC tool specifications.
"""
from app.modules.mcp.simrs_client import simrs_mcp_client
from app.modules.mcp.simrs_server import simrs_mcp_server

__all__ = ["simrs_mcp_client", "simrs_mcp_server"]
