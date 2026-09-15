import unittest
from app.modules.medical_agent.graph import medical_agent_graph, _route_validation_loop
from app.modules.medical_agent.context.state import MedicalAgentState


class TestThreeRoundLangGraphLoop(unittest.TestCase):
    """Test suite for LangGraph 3-Round Iterative Refinement & Evaluator-Optimizer Loop."""

    def test_01_route_validation_loop_routing_logic(self):
        """Test conditional edge routing for 3 rounds."""
        # Round 1 with refinement needed -> should route to synthesis (Round 2)
        state_r1: MedicalAgentState = {
            "iteration_count": 1,
            "max_iterations": 3,
            "output_validation": {"needs_refinement": True, "validation_score": 0.80},
            "hitl_required": False
        }
        self.assertEqual(_route_validation_loop(state_r1), "synthesis")

        # Round 2 with refinement needed -> should route to synthesis (Round 3)
        state_r2: MedicalAgentState = {
            "iteration_count": 2,
            "max_iterations": 3,
            "output_validation": {"needs_refinement": True, "validation_score": 0.90},
            "hitl_required": False
        }
        self.assertEqual(_route_validation_loop(state_r2), "synthesis")

        # Round 3 reached max -> must route to END
        state_r3: MedicalAgentState = {
            "iteration_count": 3,
            "max_iterations": 3,
            "output_validation": {"needs_refinement": True, "validation_score": 0.95},
            "hitl_required": False
        }
        self.assertEqual(_route_validation_loop(state_r3), "END")

        # Optimal score on round 1 (no refinement needed) -> must route to END
        state_optimal: MedicalAgentState = {
            "iteration_count": 1,
            "max_iterations": 3,
            "output_validation": {"needs_refinement": False, "validation_score": 1.0},
            "hitl_required": False
        }
        self.assertEqual(_route_validation_loop(state_optimal), "END")

        # HITL required -> must route to END immediately
        state_hitl: MedicalAgentState = {
            "iteration_count": 1,
            "max_iterations": 3,
            "output_validation": {"needs_refinement": True},
            "hitl_required": True
        }
        self.assertEqual(_route_validation_loop(state_hitl), "END")

    def test_02_graph_executes_multi_round_self_reflection(self):
        """Test invoking the medical agent graph with patient query executes self-reflection."""
        initial_state: MedicalAgentState = {
            "user_query": "Evaluasi klinis lengkap dan rekomendasi terapi obat pasien Eleanor Vance",
            "patient_id": "P-10492",
            "workflow_type": "text",
            "detected_intent": "1. Evaluasi Pasien Lengkap (Comprehensive Evaluation)",
            "max_iterations": 3,
            "iteration_count": 0,
            "steps_executed": [],
            "messages": []
        }
        config = {"configurable": {"thread_id": "test-3round-session-1"}}
        
        final_state = medical_agent_graph.invoke(initial_state, config=config)
        
        self.assertIn("iteration_count", final_state)
        self.assertGreaterEqual(final_state["iteration_count"], 1)
        self.assertLessEqual(final_state["iteration_count"], 3)
        self.assertIn("output_validation", final_state)
        self.assertTrue(final_state["output_validation"]["is_valid"])
        self.assertIn("iteration_history", final_state)
        self.assertGreaterEqual(len(final_state["iteration_history"]), 1)
        
        # Verify final output contains clinical guidance and disclaimer
        self.assertTrue("disclaimer" in final_state["final_synthesis"].lower())

    def test_03_full_three_round_execution_with_refinement(self):
        """Test that a workflow requiring refinement iterates across rounds up to round 3."""
        initial_state: MedicalAgentState = {
            "user_query": "Pasien Eleanor Vance ada indikasi infeksi, apakah boleh amoxicillin 500mg?",
            "patient_id": "P-10492",
            "workflow_type": "text",
            "detected_intent": "5. Rekomendasi Terapi Obat Berbasis Bukti (Knowledge Management)",
            "max_iterations": 3,
            "iteration_count": 0,
            "steps_executed": [],
            "messages": []
        }
        config = {"configurable": {"thread_id": "test-3round-session-refine"}}
        final_state = medical_agent_graph.invoke(initial_state, config=config)
        
        self.assertIn("iteration_count", final_state)
        self.assertGreaterEqual(final_state["iteration_count"], 1)
        self.assertIn("iteration_history", final_state)
        self.assertTrue(len(final_state["iteration_history"]) >= 1)


if __name__ == "__main__":
    unittest.main()
