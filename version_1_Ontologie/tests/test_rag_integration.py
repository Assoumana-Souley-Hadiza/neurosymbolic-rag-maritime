import pytest
from rag.core.retrievers import DenseRetriever, SparseRetriever
from rag.neo4j_ontology_agent import Neo4jOntologyAgent
from rag.integration.neo4j_bridge import Neo4jBridge
from rag.llm_generator import LLMGenerator
from batch_query_system import BatchQuerySystem

class TestRAGIntegration:
    def test_expansion_transmission(self, mocker):
        """Vérifie que les termes étendus par Neo4j sont bien passés aux retrievers."""
        # Mocks
        mock_dense = mocker.MagicMock(spec=DenseRetriever)
        mock_dense.is_ready.return_value = True
        mock_dense.retrieve.return_value = [{"id": "D1", "text": "Dense doc"}]
        
        mock_sparse = mocker.MagicMock(spec=SparseRetriever)
        mock_sparse.is_ready.return_value = True
        mock_sparse.retrieve.return_value = [{"id": "S1", "text": "Sparse doc"}]
        
        mock_agent = mocker.MagicMock(spec=Neo4jOntologyAgent)
        mock_agent.is_ready.return_value = True
        mock_agent.prepare_query.return_value = {
            "synonyms_map": {"baleine": {"baleine", "cétacé"}},
            "expanded_terms": ["baleine", "cétacé"],
            "graph_entities": set()
        }
        mock_agent.enrich.return_value = "CONTEXTE ENRICHI SIMULE"
        
        # On va instancier un BatchQuerySystem et mocker ses composants
        system = BatchQuerySystem()
        system.dense_retriever = mock_dense
        system.sparse_retriever = mock_sparse
        system.ontology_agent = mock_agent
        system.query_analyzer = mocker.MagicMock(analyze=lambda *a, **k: ("test", {}, "ben", None))
        system.fusion = mocker.MagicMock(fuse=lambda *a, **k: [{"id": "1", "text": "fused"}])
        system.llm_gen = mocker.MagicMock(model_name="mock", generate=lambda *a, **k: {"stream_generator": iter(["OK"]), "error": None})
        
        # Exécuter une requête complète
        system.interroger_question({
            "Pays": "Bénin",
            "Code_Pays": "ben",
            "Interdiction": "Chasse baleine",
            "Numero_Question": 1,
            "Question": "Est-il interdit de chasser la baleine au Bénin ?"
        })
        
        # Vérifier que dense.retrieve a été appelé avec expanded_terms contenant "cétacé"
        mock_dense.retrieve.assert_called()
        call_kwargs = mock_dense.retrieve.call_args.kwargs
        assert "expanded_terms" in call_kwargs
        assert "cétacé" in call_kwargs["expanded_terms"]
        
        # Vérifier pour le sparse
        mock_sparse.retrieve.assert_called()
        sparse_kwargs = mock_sparse.retrieve.call_args.kwargs
        assert "expanded_terms" in sparse_kwargs
        assert "cétacé" in sparse_kwargs["expanded_terms"]

    def test_enriched_context_injection(self, mocker):
        """Vérifie que le contexte enrichi par l'agent est bien passé au LLM."""
        mock_agent = mocker.MagicMock(spec=Neo4jOntologyAgent)
        mock_agent.is_ready.return_value = True
        mock_agent.enrich.return_value = "CONTEXTE ENRICHI SIMULE"
        
        mock_llm = mocker.MagicMock(spec=LLMGenerator)
        mock_llm.generate.return_value = {"stream_generator": iter(["Réponse simulée"]), "error": None}
        mock_llm.model_name = "mock_model"
        
        system = BatchQuerySystem()
        # Désactiver les autres
        system.dense_retriever = mocker.MagicMock(is_ready=lambda: True, retrieve=lambda *a, **k: [{"id": "1", "text": "test"}])
        system.sparse_retriever = None
        system.neo4j_bridge = mocker.MagicMock(is_ready=lambda: False)
        
        system.query_analyzer = mocker.MagicMock(analyze=lambda *a, **k: ("test", {}, "ben", None))
        system.fusion = mocker.MagicMock(fuse=lambda *a, **k: [{"id": "1", "text": "fused"}])
        
        system.ontology_agent = mock_agent
        system.llm_gen = mock_llm
        
        system.interroger_question({
            "Pays": "Bénin", "Code_Pays": "ben", "Interdiction": "Test",
            "Numero_Question": 1, "Question": "Test question"
        })
        
        # Vérifier que le LLM a bien reçu le contexte enrichi dans la méthode generate()
        mock_llm.generate.assert_called()
        llm_kwargs = mock_llm.generate.call_args.kwargs
        assert "enriched_context" in llm_kwargs
        assert llm_kwargs["enriched_context"] == "CONTEXTE ENRICHI SIMULE"
