import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token
from app.modules.rag.bm25 import BM25Engine
from app.modules.rag.rag_service import qdrant_rag_service
from app.modules.medical_agent.tools.rag_tools import tool_vector_rag_search


class TestBM25VectorHybridSearch(unittest.TestCase):
    """Test suite for BM25 Sparse Ranking, Qdrant Dense Vector Search, and Threshold > 0.5 Filtering."""

    def setUp(self):
        self.client = TestClient(app)
        token = create_access_token("admin-1", "admin@AssistantMedixa.com", "admin")
        self.headers = {"Authorization": f"Bearer {token}"}

    def test_01_bm25_engine_indexing_and_scoring(self):
        """Test standalone BM25Engine term-frequency scoring and length normalization."""
        engine = BM25Engine(k1=1.5, b=0.75)
        chunks = [
            {
                "chunk_id": "test-c1",
                "title": "Gastritis Erosif Kronis",
                "category": "disease",
                "specialty": "Gastroenterology",
                "icd10_code": "K29.1",
                "keywords": ["gastritis", "omeprazole", "lambung", "sukralfat"],
                "chunk_text": "Pasien dengan gastritis erosif mengalami nyeri ulu hati dan mual. Terapi utama omeprazole."
            },
            {
                "chunk_id": "test-c2",
                "title": "Diabetes Melitus Tipe 2",
                "category": "disease",
                "specialty": "Endocrinology",
                "icd10_code": "E11.9",
                "keywords": ["diabetes", "metformin", "hba1c", "insulin"],
                "chunk_text": "Diabetes tipe 2 ditandai hiperglikemia kronis. Terapi lini pertama metformin 500mg."
            }
        ]
        engine.index_chunks(chunks)
        self.assertEqual(engine.total_docs, 2)
        
        # Search for gastritis
        scores = engine.get_normalized_scores("nyeri lambung gastritis omeprazole")
        self.assertIn("test-c1", scores)
        self.assertIn("test-c2", scores)
        self.assertGreater(scores["test-c1"], scores["test-c2"])
        self.assertGreater(scores["test-c1"], 0.3)

    def test_02_hybrid_qdrant_and_bm25_search_returns_relevant_results(self):
        """Test hybrid search combines vector and BM25 signals with threshold > 0.5."""
        query = "Gastritis Kronis Erosif nyeri ulu hati lambung omeprazole"
        results = qdrant_rag_service.search(query=query, top_k=3, similarity_threshold=0.5)
        
        self.assertGreater(len(results), 0, "Hybrid search must return relevant results for Gastritis query")
        for item in results:
            self.assertGreater(item["reranked_score"], 0.5, f"All returned chunks must have similarity score > 0.5, got {item['reranked_score']}")
            self.assertIn("vector_score", item)
            self.assertIn("bm25_score", item)
            self.assertGreaterEqual(item["bm25_score"], 0.0)
            
        top_title = results[0]["payload"]["title"]
        self.assertTrue(
            "Gastritis" in top_title or "Omeprazole" in top_title or "Sukralfat" in top_title,
            f"Top result should match Gastritis/PPI/Sucralfate, got {top_title}"
        )

    def test_03_threshold_filtering_excludes_irrelevant_noise(self):
        """Test that random irrelevant query produces no results because similarity <= 0.5 threshold."""
        query = "xyz987quantumxyzgibberishnoise123456"
        results = qdrant_rag_service.search(query=query, top_k=5, similarity_threshold=0.5)
        
        self.assertEqual(len(results), 0, "Irrelevant query must be filtered out by threshold > 0.5")

    def test_04_tool_vector_rag_search_with_bm25_metrics(self):
        """Test tool_vector_rag_search formats BM25 and vector scores."""
        chunks = tool_vector_rag_search("Diabetes T2DM metformin renal dosing", top_k=2, similarity_threshold=0.5)
        self.assertGreater(len(chunks), 0)
        for c in chunks:
            self.assertGreater(c["reranked_score"], 0.5)
            self.assertIn("bm25_score", c)
            self.assertIn("vector_score", c)

    def test_05_api_rag_search_endpoint_with_bm25(self):
        """Test /api/v1/rag/search endpoint returns BM25 enriched results above threshold 0.5."""
        res = self.client.post(
            "/api/v1/rag/search",
            json={
                "query": "CAD Post-PCI clopidogrel stent isdn bisoprolol",
                "top_k": 3,
                "similarity_threshold": 0.5
            },
            headers=self.headers
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertGreater(data["results_count"], 0)
        for chunk in data["chunks"]:
            self.assertGreater(chunk["reranked_score"], 0.5)


if __name__ == "__main__":
    unittest.main()
