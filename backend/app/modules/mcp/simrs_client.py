from typing import Dict, Any, List, Optional
import logging
from app.modules.mcp.simrs_server import simrs_mcp_server

logger = logging.getLogger("mcp.client")


class SIMRSMCPClientBridge:
    """Dynamic Client Bridge connecting external callers or LangGraph agent tools to MCP Server."""
    
    def __init__(self):
        self.server = simrs_mcp_server

    # ── Dynamic Tool Discovery Methods ──────────────────────────────

    def get_available_mcp_tools(self) -> List[Dict[str, Any]]:
        """Queries MCP Server for currently registered and active tools."""
        return self.server.list_tools()

    def get_tool_names(self) -> List[str]:
        """Returns list of active tool identifier names from MCP Server."""
        tools = self.get_available_mcp_tools()
        return [t.get("name", "") for t in tools if t.get("name")]

    def get_tool_declaration(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Finds and returns the declaration and input schema for a given tool name."""
        tools = self.get_available_mcp_tools()
        for t in tools:
            if t.get("name") == tool_name:
                return t
        return None

    def is_tool_available(self, tool_name: str) -> bool:
        """Checks whether a specific tool is registered and currently active."""
        return tool_name in self.get_tool_names()

    # ── Dynamic Tool Execution Methods ──────────────────────────────

    def execute_tool(self, tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Dynamically executes any MCP tool by name with arguments validation."""
        args = arguments or {}
        
        # Verify tool is available in active MCP tools list
        if not self.is_tool_available(tool_name):
            logger.warning("MCP Tool '%s' is requested but not currently available in active tools list.", tool_name)
            return {
                "status": "error",
                "message": f"MCP Tool '{tool_name}' tidak ditemukan atau sedang dinonaktifkan oleh Administrator.",
                "tool_name": tool_name,
                "is_enabled": False
            }

        return self.server.call_tool(tool_name, args)

    def call_tool(self, tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Alias for execute_tool."""
        return self.execute_tool(tool_name, arguments)

    def invoke(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Convenience method to execute a tool using keyword arguments."""
        return self.execute_tool(tool_name, kwargs)

    def _resolve_tool_name(self, name: str) -> Optional[str]:
        """Resolves various Python method naming styles to the actual registered MCP tool name.
        
        Supports:
            - Exact match: 'simrs.get_patient_profile'
            - Dot-prefix shorthand: 'get_patient_profile' -> 'simrs.get_patient_profile'
            - Snake-case prefix: 'simrs_get_patient_profile' -> 'simrs.get_patient_profile'
            - Generic namespace conversion: 'hospital_check_stock' -> 'hospital.check_stock'
        """
        active_names = self.get_tool_names()
        
        # 1. Exact match
        if name in active_names:
            return name
            
        # 2. Try prepending default 'simrs.' namespace
        simrs_candidate = f"simrs.{name}"
        if simrs_candidate in active_names:
            return simrs_candidate
            
        # 3. Try converting leading underscore to dot (e.g. simrs_get_patient_profile -> simrs.get_patient_profile)
        dot_candidate = name.replace("_", ".", 1)
        if dot_candidate in active_names:
            return dot_candidate
            
        # 4. Search case-insensitive suffix match
        for tool_name in active_names:
            suffix = tool_name.split(".")[-1]
            if suffix == name or tool_name.replace(".", "_") == name:
                return tool_name
                
        return None

    def __getattr__(self, name: str):
        """Dynamically intercepts and dispatches any tool method call to the MCP Server.
        
        Supports both positional and keyword arguments mapped to the tool's JSON input schema.
        
        Examples:
            client.get_patient_profile("P-10492")
            client.get_patient_profile(mrn="P-10492")
            client.simrs_get_patient_labs(mrn="P-20811")
            client.update_patient_record("P-10492", notes, diag, plan)
            client.hospital_custom_tool(query="...")
        """
        if name.startswith("_"):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        resolved_tool_name = self._resolve_tool_name(name)
        if not resolved_tool_name:
            raise AttributeError(f"'{self.__class__.__name__}' object has no registered MCP tool matching '{name}'")

        def _dynamic_tool_caller(*args, **kwargs) -> Dict[str, Any]:
            declaration = self.get_tool_declaration(resolved_tool_name) or {}
            schema = declaration.get("inputSchema", declaration.get("input_schema", {}))
            props = list(schema.get("properties", {}).keys())

            # Bind positional args to schema property names in declared order
            merged_arguments = {}
            for i, val in enumerate(args):
                if i < len(props):
                    merged_arguments[props[i]] = val

            # Merge with explicitly passed keyword arguments
            merged_arguments.update(kwargs)

            return self.execute_tool(resolved_tool_name, merged_arguments)

        return _dynamic_tool_caller

    def __dir__(self):
        """Includes all currently active dynamic MCP tools in dir() reflection."""
        base_attrs = super().__dir__()
        dynamic_tool_methods = [
            t.replace(".", "_") for t in self.get_tool_names()
        ] + [
            t.split(".")[-1] for t in self.get_tool_names()
        ]
        return sorted(set(base_attrs + dynamic_tool_methods))



simrs_mcp_client = SIMRSMCPClientBridge()

