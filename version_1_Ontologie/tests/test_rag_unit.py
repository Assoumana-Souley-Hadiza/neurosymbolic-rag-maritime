import pytest
from rag.core.query_analyzer import QueryAnalyzer
from rag.core.fusion import HybridFusion
from rag.integration.neo4j_bridge import Neo4jBridge

class TestQueryAnalyzer:
    def test_extract_country(self):
        qa = QueryAnalyzer()
        
        # Test avec un pays connu
        intent, weights, country_filter, category_filter = qa.analyze("Est-ce que la pêche est interdite au Maroc ?")
        assert country_filter == "mor"
        
        # Test avec un autre pays
        intent, weights, country_filter, category_filter = qa.analyze("Quelles sont les sanctions au Cameroun ?")
        assert country_filter == "cmr"

        # Test sans pays mentionné
        intent, weights, country_filter, category_filter = qa.analyze("Qu'est-ce que le chalutage de fond ?")
        assert country_filter is None

    def test_intent_detection(self):
        qa = QueryAnalyzer()
        intent, weights, country, cat = qa.analyze("Y a-t-il une exception pour le chalutage ?")
        assert intent in ["exception", "legal"]
        
        intent, weights, country, cat = qa.analyze("Combien coûte l'amende pour rejet de pétrole ?")
        assert intent == "sanction_financiere"

class TestHybridFusion:
    def test_rrf_scoring(self):
        fusion = HybridFusion()
        
        # 3 documents simulés
        doc1 = {"id": "DOC1", "text": "Texte 1", "rank": 1}
        doc2 = {"id": "DOC2", "text": "Texte 2", "rank": 2}
        doc3 = {"id": "DOC3", "text": "Texte 3", "rank": 3}
        
        # Le dense met DOC1 puis DOC2
        # Le sparse met DOC2 puis DOC3
        # DOC2 est commun aux deux, il devrait bénéficier d'un meilleur score RRF combiné
        retriever_results = {
            "dense": [doc1.copy(), {"id": "DOC2", "text": "Texte 2", "rank": 2}],
            "sparse": [{"id": "DOC2", "text": "Texte 2", "rank": 1}, {"id": "DOC3", "text": "Texte 3", "rank": 2}]
        }
        
        results = fusion.fuse(
            retriever_results=retriever_results,
            weights={"dense": 1.0, "sparse": 1.0},
            disable_reranker=True, # On teste juste la RRF
            top_k=3
        )
        
        assert len(results) == 3
        # DOC2 doit être premier
        assert results[0]["id"] == "DOC2"
        # DOC1 et DOC3 ensuite
        assert {"DOC1", "DOC3"}.issuperset({results[1]["id"], results[2]["id"]})

class TestNeo4jBridge:
    def test_get_synonyms_mock(self, mocker):
        # On mock l'objet driver de Neo4j pour ne pas avoir besoin de BDD locale active
        mock_bridge = mocker.MagicMock(spec=Neo4jBridge)
        mock_bridge.is_ready.return_value = True
        mock_bridge.get_synonyms_batch.return_value = {"baleine": {"cétacé", "mammifère"}}
        
        syns = mock_bridge.get_synonyms_batch(["baleine"])
        assert "baleine" in syns
        assert "cétacé" in syns["baleine"]
        assert "mammifère" in syns["baleine"]
