import pytest
from rag.integration.neo4j_bridge_safe import Neo4jBridgeSafe
from rag.core.fusion import HybridFusion
from rag.core.query_analyzer import QueryAnalyzer

class TestRAGRobustness:
    def test_query_no_synonyms(self, mocker):
        from batch_query_system import BatchQuerySystem
        system = BatchQuerySystem()
        
        # Mocker Neo4j pour renvoyer des ensembles vides
        mock_bridge = mocker.MagicMock()
        mock_bridge.is_ready.return_value = True
        mock_bridge.get_synonyms_batch.return_value = {}
        mock_bridge.get_interdictions_by_keywords.return_value = []
        mock_bridge.get_entity_labels_for_query.return_value = set()
        system.neo4j_bridge = mock_bridge
        
        system.dense_retriever = mocker.MagicMock(is_ready=lambda: True, retrieve=lambda *a, **k: [{"id": "1", "text": "test"}])
        system.sparse_retriever = None
        system.ontology_agent = None
        
        system.query_analyzer = mocker.MagicMock(analyze=lambda *a, **k: ("test", {}, "ben", None))
        system.fusion = mocker.MagicMock(fuse=lambda *a, **k: [{"id": "1", "text": "fused"}])
        
        mock_llm = mocker.MagicMock()
        mock_llm.model_name = "mock"
        mock_llm.generate.side_effect = lambda *a, **k: {"stream_generator": iter(["OK"]), "error": None}
        system.llm_gen = mock_llm

        res = system.interroger_question({
            "Pays": "Bénin", "Code_Pays": "ben", "Interdiction": "Test",
            "Numero_Question": 1, "Question": "Question sans mots clés ?"
        })
        
        # Le pipeline ne doit pas crasher
        assert not res.get("Erreur")
        assert res["Reponse_Neurosymbolique"] == "OK"

    def test_neo4j_fallback(self, mocker):
        # On simule un crash réseau lors de l'initialisation du vrai Neo4jBridge
        # Neo4jBridgeSafe devrait intercepter l'erreur et se marquer "not ready" au lieu de crasher l'appli.
        from neo4j.exceptions import ServiceUnavailable
        mocker.patch("rag.integration.neo4j_bridge.Neo4jBridge.__init__", side_effect=ServiceUnavailable("Connection refused"))
        
        # Initialisation du safe bridge
        safe_bridge = Neo4jBridgeSafe()
        
        # Il ne doit pas crasher, mais is_ready() doit être False
        assert safe_bridge.is_ready() is False
        
        # Un appel à une fonction doit renvoyer une valeur par défaut silencieusement
        assert safe_bridge.get_synonyms_batch(["test"]) == {"test": {"test"}}
        
    def test_absurd_query_fusion(self):
        # Une requête sans retriever_results devrait retourner une liste vide, sans planter
        fusion = HybridFusion()
        res = fusion.fuse(
            retriever_results={},
            weights={},
            synonym_sets={},
            top_k=5
        )
        assert res == []
