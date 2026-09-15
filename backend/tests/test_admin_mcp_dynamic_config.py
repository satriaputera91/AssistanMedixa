import unittest
from datetime import datetime
from app.core.database import dbApplication
from app.modules.mcp.simrs_server import simrs_mcp_server
from app.modules.admin.schemas import (
    UpdateMCPConfigRequest,
    CreateCustomMCPToolRequest,
    UpdateMCPToolRequest,
    MCPTestRunToolRequest
)


class TestAdminMCPDynamicConfig(unittest.TestCase):
    """Test suite for Admin Dynamic MCP Configuration and Tools Management."""

    def test_01_get_and_update_mcp_config(self):
        """Test retrieving and updating MCP server configuration."""
        cfg = dbApplication.get_mcp_config()
        self.assertIn("server_name", cfg)
        self.assertIn("mode", cfg)
        self.assertEqual(cfg["protocol_version"], "2024-11-05")

        # Update config
        updated = dbApplication.update_mcp_config({
            "mode": "hybrid",
            "timeout_seconds": 15,
            "retry_attempts": 5
        })
        self.assertEqual(updated["mode"], "hybrid")
        self.assertEqual(updated["timeout_seconds"], 15)
        self.assertEqual(updated["retry_attempts"], 5)

        # Restore default
        dbApplication.update_mcp_config({"mode": "mock", "timeout_seconds": 10, "retry_attempts": 3})

    def test_02_dynamic_tool_listing_reflects_active_status(self):
        """Test that simrs_mcp_server.list_tools() dynamically reflects active/inactive tools."""
        all_tools = dbApplication.get_all_mcp_tools()
        self.assertGreaterEqual(len(all_tools), 5)

        # Initially, all builtin tools are active
        active_tools = simrs_mcp_server.list_tools()
        active_names = [t["name"] for t in active_tools]
        self.assertIn("simrs.get_patient_anamnesis", active_names)

        # Disable simrs.get_patient_anamnesis
        toggled = dbApplication.toggle_mcp_tool_status("simrs.get_patient_anamnesis")
        self.assertFalse(toggled["is_enabled"])

        # Check list_tools no longer returns it
        updated_active_tools = simrs_mcp_server.list_tools()
        updated_names = [t["name"] for t in updated_active_tools]
        self.assertNotIn("simrs.get_patient_anamnesis", updated_names)

        # Call tool should return disabled error
        res = simrs_mcp_server.call_tool("simrs.get_patient_anamnesis", {"mrn": "P-10492"})
        self.assertEqual(res["status"], "error")
        self.assertIn("dinonaktifkan", res["message"])

        # Re-enable tool
        re_enabled = dbApplication.toggle_mcp_tool_status("simrs.get_patient_anamnesis")
        self.assertTrue(re_enabled["is_enabled"])

        restored_active = simrs_mcp_server.list_tools()
        self.assertIn("simrs.get_patient_anamnesis", [t["name"] for t in restored_active])

    def test_03_create_update_and_delete_custom_mcp_tool(self):
        """Test creating, updating, executing, and deleting a custom MCP tool."""
        custom_tool_name = "hospital.check_pharmacy_stock"
        
        # 1. Create custom tool
        new_tool = dbApplication.create_custom_mcp_tool({
            "name": custom_tool_name,
            "display_name": "Cek Stok Farmasi Rumah Sakit",
            "description": "Memeriksa ketersediaan stok obat di instalasi farmasi RS.",
            "category": "pharmacy",
            "is_enabled": True,
            "input_schema": {
                "type": "object",
                "properties": {
                    "drug_name": {"type": "string", "description": "Nama obat"}
                },
                "required": ["drug_name"]
            },
            "mock_response": {
                "available": True,
                "stock_units": 150,
                "warehouse": "Gudang Farmasi Utama"
            }
        })
        self.assertEqual(new_tool["name"], custom_tool_name)
        self.assertFalse(new_tool["is_builtin"])

        # 2. Verify tool is in list_tools
        active_tools = simrs_mcp_server.list_tools()
        self.assertIn(custom_tool_name, [t["name"] for t in active_tools])

        # 3. Execute tool
        exec_res = simrs_mcp_server.call_tool(custom_tool_name, {"drug_name": "Metformin 500mg"})
        self.assertEqual(exec_res["status"], "success")
        self.assertIn("result", exec_res)
        self.assertTrue(exec_res["result"]["available"])

        # 4. Verify execution counter incremented
        tool_meta = dbApplication.get_mcp_tool(custom_tool_name)
        self.assertEqual(tool_meta["execution_count"], 1)
        self.assertIsNotNone(tool_meta["last_executed_at"])

        # 5. Update tool display name
        updated = dbApplication.update_mcp_tool(custom_tool_name, {"display_name": "Pemeriksaan Stok Obat Farmasi"})
        self.assertEqual(updated["display_name"], "Pemeriksaan Stok Obat Farmasi")

        # 6. Delete custom tool
        deleted = dbApplication.delete_mcp_tool(custom_tool_name)
        self.assertTrue(deleted)
        self.assertIsNone(dbApplication.get_mcp_tool(custom_tool_name))

    def test_04_builtin_tools_cannot_be_deleted(self):
        """Test that builtin tools cannot be deleted, but raise ValueError."""
        with self.assertRaises(ValueError):
            dbApplication.delete_mcp_tool("simrs.get_patient_profile")

    def test_05_dynamic_simrs_mcp_client_bridge(self):
        """Test dynamic tool discovery and execution via SIMRSMCPClientBridge."""
        from app.modules.mcp.simrs_client import simrs_mcp_client

        # 1. Discover available tools & names
        available = simrs_mcp_client.get_available_mcp_tools()
        names = simrs_mcp_client.get_tool_names()
        self.assertGreaterEqual(len(available), 5)
        self.assertIn("simrs.get_patient_profile", names)
        self.assertIn("simrs.get_patient_labs", names)

        # 2. Check tool declaration schema
        schema = simrs_mcp_client.get_tool_declaration("simrs.get_patient_profile")
        self.assertIsNotNone(schema)
        self.assertEqual(schema["name"], "simrs.get_patient_profile")
        self.assertIn("inputSchema", schema)

        # 3. Test is_tool_available
        self.assertTrue(simrs_mcp_client.is_tool_available("simrs.get_patient_profile"))
        self.assertFalse(simrs_mcp_client.is_tool_available("non_existent_tool_xyz"))

        # 4. Test dynamic execution via execute_tool / invoke
        profile_res = simrs_mcp_client.execute_tool("simrs.get_patient_profile", {"mrn": "P-10492"})
        self.assertEqual(profile_res["status"], "success")
        self.assertIn("profile", profile_res)
        self.assertEqual(profile_res["profile"]["mrn"], "MRN-SIMRS-10492")

        # 5. Test invoke keyword arguments
        labs_res = simrs_mcp_client.invoke("simrs.get_patient_labs", mrn="P-10492")
        self.assertEqual(labs_res["status"], "success")
        self.assertIn("latest_labs", labs_res)

        # 6. Test dynamic attribute caller client.simrs_get_patient_profile(mrn="P-10492")
        dyn_profile = simrs_mcp_client.simrs_get_patient_profile(mrn="P-10492")
        self.assertEqual(dyn_profile["status"], "success")

        # 7. Test execution of disabled tool returns graceful error response
        dbApplication.toggle_mcp_tool_status("simrs.get_patient_anamnesis")
        disabled_res = simrs_mcp_client.execute_tool("simrs.get_patient_anamnesis", {"mrn": "P-10492"})
        self.assertEqual(disabled_res["status"], "error")
        self.assertIn("dinonaktifkan", disabled_res["message"])

        # Restore tool status
        dbApplication.toggle_mcp_tool_status("simrs.get_patient_anamnesis")


if __name__ == "__main__":
    unittest.main()
