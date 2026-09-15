from typing import Dict, Any, List, Optional, Tuple
import logging
from app.core.config import settings
from app.modules.mcp.simrs_client import simrs_mcp_client

logger = logging.getLogger("mcp.gemini_function_calling")

try:
    from google import genai
    from google.genai import types
    HAS_GOOGLE_GENAI_SDK = True
except ImportError:
    HAS_GOOGLE_GENAI_SDK = False


class MCPGeminiFunctionAdapter:
    """Adapter bridging MCP (Model Context Protocol) tool declarations to  Generative AI Function Calling."""

    @staticmethod
    def normalize_tool_name_for_gemini(mcp_name: str) -> str:
        """Converts MCP dot/dash notation into a valid Generative AI identifier (alphanumeric/underscore).
        Example: 'simrs.get_patient_profile' -> 'simrs_get_patient_profile'
        """
        return mcp_name.replace(".", "_").replace("-", "_")

    @staticmethod
    def resolve_mcp_tool_name(gemini_func_name: str) -> str:
        """Resolves a Generative AI function call identifier back to its original MCP tool name."""
        active_tools = simrs_mcp_client.get_available_mcp_tools()
        # Direct match
        for t in active_tools:
            name = t.get("name", "")
            if name == gemini_func_name or MCPGeminiFunctionAdapter.normalize_tool_name_for_gemini(name) == gemini_func_name:
                return name

        # Fallback to dot conversion
        return gemini_func_name.replace("_", ".", 1)

    @classmethod
    def convert_schema_to_gemini_parameters(cls, input_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Ensures input JSON schema matches Generative AI's expected types."""
        if not input_schema:
            return {"type": "OBJECT", "properties": {}}

        schema = dict(input_schema)
        # Deep copy/format properties
        raw_props = schema.get("properties", {})
        formatted_props = {}
        for prop_name, prop_def in raw_props.items():
            p_type = str(prop_def.get("type", "STRING")).upper()
            formatted_props[prop_name] = {
                "type": p_type,
                "description": prop_def.get("description", f"Parameter {prop_name}")
            }
        
        return {
            "type": "OBJECT",
            "properties": formatted_props,
            "required": schema.get("required", list(formatted_props.keys()))
        }

    @classmethod
    def get_gemini_function_declarations(cls) -> List[Dict[str, Any]]:
        """Generates list of Generative AI-compatible Function Declarations from all active MCP tools."""
        active_tools = simrs_mcp_client.get_available_mcp_tools()
        declarations = []

        for tool in active_tools:
            raw_name = tool.get("name", "")
            gemini_name = cls.normalize_tool_name_for_gemini(raw_name)
            desc = tool.get("description", f"MCP Tool: {raw_name}")
            schema = cls.convert_schema_to_gemini_parameters(tool.get("inputSchema", tool.get("input_schema", {})))

            declarations.append({
                "name": gemini_name,
                "description": desc,
                "parameters": schema,
                "original_mcp_name": raw_name
            })

        return declarations

    @classmethod
    def build_genai_sdk_tools(cls) -> List[Any]:
        """Builds types.Tool instance containing function declarations for the  GenAI SDK."""
        if not HAS_GOOGLE_GENAI_SDK:
            return []

        decls = cls.get_gemini_function_declarations()
        sdk_function_declarations = []

        for d in decls:
            try:
                sdk_fd = types.FunctionDeclaration(
                    name=d["name"],
                    description=d["description"],
                    parameters=d["parameters"]
                )
                sdk_function_declarations.append(sdk_fd)
            except Exception as e:
                logger.warning("Failed to build FunctionDeclaration for %s: %s", d["name"], e)

        if not sdk_function_declarations:
            return []

        return [types.Tool(function_declarations=sdk_function_declarations)]

    @classmethod
    def execute_gemini_function_call(cls, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Executes a function call requested by Generative AI and maps it to the MCP Server."""
        mcp_name = cls.resolve_mcp_tool_name(function_name)
        logger.info("Executing Generative AI Function Call '%s' -> MCP Tool '%s' with args %s", function_name, mcp_name, arguments)
        
        result = simrs_mcp_client.execute_tool(mcp_name, arguments)
        return {
            "function_name": function_name,
            "mcp_tool_name": mcp_name,
            "status": result.get("status", "success"),
            "result": result
        }


class GeminiMCPService:
    """Service to execute clinical queries with Generative AI LLM using dynamic MCP Function Calling."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model_name or settings.GEMINI_MODEL_NAME

    def run_query_with_mcp_function_calling(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        patient_id: Optional[str] = None,
        max_tool_calls: int = 5
    ) -> Dict[str, Any]:
        """Executes Generative AI LLM with dynamic MCP tools, automatically resolving and executing tool calls."""
        executed_tool_calls = []
        final_text = ""

        if not self.api_key or not HAS_GOOGLE_GENAI_SDK:
            logger.info(" GenAI SDK or API key not present, falling back to direct MCP execution.")
            # Fallback direct query
            active_tools = simrs_mcp_client.get_available_mcp_tools()
            return {
                "status": "fallback",
                "final_text": f"Kueri klinis diproses menggunakan MCP Tools aktif ({len(active_tools)} tools).",
                "executed_tool_calls": executed_tool_calls
            }

        try:
            client = genai.Client(api_key=self.api_key)
            tools = MCPGeminiFunctionAdapter.build_genai_sdk_tools()

            sys_inst = system_instruction or (
                "Anda adalah AI Medical Clinical Assistant. Gunakan tool SIMRS / Satu Sehat yang tersedia "
                "untuk memeriksa profil pasien, riwayat medis, hasil laboratorium, atau memperbarui rekam medis "
                "bila diperlukan untuk menjawab pertanyaan klinis secara akurat dan berbasis bukti."
            )

            config = types.GenerateContentConfig(
                system_instruction=sys_inst,
                tools=tools,
                temperature=0.2,
            )

            # Initial call to Generative AI with tools enabled
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )

            # Check for function calls from Generative AI
            function_calls = getattr(response, "function_calls", None)
            
            if function_calls:
                # Loop through each tool call requested by Generative AI
                for fc in function_calls[:max_tool_calls]:
                    func_name = getattr(fc, "name", "")
                    func_args = getattr(fc, "args", {})
                    if hasattr(func_args, "model_dump"):
                        func_args = func_args.model_dump()
                    elif not isinstance(func_args, dict):
                        func_args = dict(func_args)

                    # Auto-inject patient MRN if missing and patient_id is provided
                    if patient_id and "mrn" in func_args and not func_args["mrn"]:
                        func_args["mrn"] = patient_id

                    exec_res = MCPGeminiFunctionAdapter.execute_gemini_function_call(func_name, func_args)
                    executed_tool_calls.append(exec_res)

                # Generate final grounded synthesis after function calls
                tools_summary_str = "\n\n".join(
                    f"--- HASIL EKSEKUSI MCP TOOL: {tc['mcp_tool_name']} ---\n{tc['result']}"
                    for tc in executed_tool_calls
                )
                
                follow_up_prompt = f"{prompt}\n\n[INFORMASI DARI TOOLS MCP SIMRS]:\n{tools_summary_str}\n\nSintesiskan jawaban klinis lengkap berdasarkan data di atas."
                
                synthesis_res = client.models.generate_content(
                    model=self.model_name,
                    contents=follow_up_prompt,
                    config=types.GenerateContentConfig(system_instruction=sys_inst, temperature=0.2)
                )
                final_text = (synthesis_res.text or "").strip()
            else:
                final_text = (response.text or "").strip()

            return {
                "status": "success",
                "final_text": final_text,
                "executed_tool_calls": executed_tool_calls,
                "tools_count": len(tools[0].function_declarations) if tools and tools[0].function_declarations else 0
            }

        except Exception as e:
            logger.error("Error in Generative AI MCP Function Calling: %s", e, exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "final_text": f"Gagal mengeksekusi Generative AI Function Calling: {str(e)}",
                "executed_tool_calls": executed_tool_calls
            }


gemini_mcp_service = GeminiMCPService()
