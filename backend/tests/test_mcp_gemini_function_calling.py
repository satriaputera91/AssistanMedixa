import unittest
from app.core.database import dbApplication
from app.modules.medical_agent.mcp_function_calling import (
    MCPGeminiFunctionAdapter,
    gemini_mcp_service,
    GeminiMCPService,
)
from app.modules.medical_agent.tools.simrs_tools import (
    get_active_mcp_tools,
    get_gemini_mcp_function_declarations,
    execute_mcp_tool_dynamically,
    execute_gemini_function_call,
    run_gemini_with_mcp_tools,
)


class TestMCPGeminiFunctionCalling(unittest.TestCase):
    """Test suite for Dynamic MCP Function Calling via  Generative AI."""

    def test_01_name_normalization_and_resolution(self):
        """Test normalizing MCP dot names to Generative AI names and resolving back."""
        mcp_name = "simrs.get_patient_profile"
        gemini_name = MCPGeminiFunctionAdapter.normalize_tool_name_for_gemini(mcp_name)
        self.assertEqual(gemini_name, "simrs_get_patient_profile")

        resolved = MCPGeminiFunctionAdapter.resolve_mcp_tool_name(gemini_name)
        self.assertEqual(resolved, mcp_name)

    def test_02_dynamic_gemini_function_declarations(self):
        """Test generating Generative AI Function Declarations from active MCP tools."""
        declarations = get_gemini_mcp_function_declarations()
        self.assertGreaterEqual(len(declarations), 5)

        names = [d["name"] for d in declarations]
        self.assertIn("simrs_get_patient_profile", names)
        self.assertIn("simrs_get_patient_history", names)
        self.assertIn("simrs_get_patient_labs", names)

        # Check parameter schema format
        profile_decl = next(d for d in declarations if d["name"] == "simrs_get_patient_profile")
        self.assertEqual(profile_decl["parameters"]["type"], "OBJECT")
        self.assertIn("mrn", profile_decl["parameters"]["properties"])

    def test_03_execute_gemini_function_call(self):
        """Test executing function call by Generative AI name."""
        res = execute_gemini_function_call("simrs_get_patient_profile", {"mrn": "P-10492"})
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["mcp_tool_name"], "simrs.get_patient_profile")
        self.assertIn("result", res)
        self.assertEqual(res["result"]["profile"]["mrn"], "MRN-SIMRS-10492")

    def test_04_dynamic_mcp_tool_execution(self):
        """Test executing tool dynamically through simrs_tools wrapper."""
        res = execute_mcp_tool_dynamically("simrs.get_patient_labs", mrn="P-20811")
        self.assertEqual(res["status"], "success")
        self.assertIn("latest_labs", res)

    def test_05_custom_mcp_tool_reflects_in_gemini_declarations(self):
        """Test that adding a custom tool dynamically creates a Generative AI function declaration."""
        custom_name = "hospital.lab_culture_test"
        dbApplication.create_custom_mcp_tool({
            "name": custom_name,
            "display_name": "Uji Kultur & Sensitivitas Lab",
            "description": "Pemeriksaan kultur bakteri dan uji resistensi antibiotik.",
            "category": "laboratory",
            "input_schema": {
                "type": "object",
                "properties": {
                    "specimen_id": {"type": "string", "description": "ID Spesimen"}
                },
                "required": ["specimen_id"]
            },
            "mock_response": {
                "isolated_organism": "E. coli",
                "sensitivity": ["Ciprofloxacin", "Amikacin"],
                "resistant": ["Ampicillin"]
            }
        })

        decls = get_gemini_mcp_function_declarations()
        gemini_names = [d["name"] for d in decls]
        self.assertIn("hospital_lab_culture_test", gemini_names)

        # Execute custom function call
        res = execute_gemini_function_call("hospital_lab_culture_test", {"specimen_id": "SPEC-001"})
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["result"]["result"]["isolated_organism"], "E. coli")

        # Clean up
        dbApplication.delete_mcp_tool(custom_name)

    def test_06_build_genai_sdk_tools(self):
        """Test building types.Tool for  GenAI SDK."""
        tools = MCPGeminiFunctionAdapter.build_genai_sdk_tools()
        self.assertIsInstance(tools, list)
        if tools:
            self.assertGreaterEqual(len(tools[0].function_declarations), 5)

    def test_07_single_tool_simrs_get_patient(self):
        """Test the consolidated single get function tool_simrs_get_patient with data_type."""
        from app.modules.medical_agent.tools.simrs_tools import (
            tool_simrs_get_patient,
            tool_simrs_get_patient_data,
            tool_simrs_get_patient_profile,
            tool_simrs_get_patient_history,
            tool_simrs_get_patient_anamnesis,
            tool_simrs_get_patient_labs,
        )

        mrn = "P-10492"

        # 1. Default (Profile / Demographics)
        prof_default = tool_simrs_get_patient(mrn)
        self.assertEqual(prof_default["status"], "success")
        self.assertEqual(prof_default["profile"]["mrn"], "MRN-SIMRS-10492")

        # 2. Specific data_type="profile"
        prof = tool_simrs_get_patient(mrn, data_type="profile")
        self.assertEqual(prof["status"], "success")

        # 3. History
        hist = tool_simrs_get_patient(mrn, data_type="history")
        self.assertEqual(hist["status"], "success")
        self.assertIn("history", hist)

        # 4. Anamnesis
        anam = tool_simrs_get_patient(mrn, data_type="anamnesis")
        self.assertEqual(anam["status"], "success")
        self.assertIn("anamnesis", anam)

        # 5. Labs & Vitals
        labs = tool_simrs_get_patient(mrn, data_type="labs")
        self.assertEqual(labs["status"], "success")
        self.assertIn("latest_labs", labs)

        # 6. Combined / Comprehensive 'all'
        all_data = tool_simrs_get_patient(mrn, data_type="all")
        self.assertEqual(all_data["status"], "success")
        self.assertIn("profile", all_data)
        self.assertIn("history", all_data)
        self.assertIn("anamnesis", all_data)
        self.assertIn("labs", all_data)

        # 7. Backward compatible aliases
        self.assertEqual(tool_simrs_get_patient_data(mrn, data_type="profile")["status"], "success")
        self.assertEqual(tool_simrs_get_patient_profile(mrn)["status"], "success")
        self.assertEqual(tool_simrs_get_patient_history(mrn)["status"], "success")
        self.assertEqual(tool_simrs_get_patient_anamnesis(mrn)["status"], "success")
        self.assertEqual(tool_simrs_get_patient_labs(mrn)["status"], "success")


if __name__ == "__main__":
    unittest.main()
