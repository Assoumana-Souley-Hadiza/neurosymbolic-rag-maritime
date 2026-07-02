#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test rapide - Démo du système RAG

Exécute quelques questions de test pour vérifier que le système fonctionne
avant de lancer le batch complet (1056 questions).

Usage:
    python test_quick_query.py                   # Test avec 6 questions
    python test_quick_query.py --verbose         # Mode verbose
"""

import sys
import logging
from pathlib import Path

# Ajouter le dossier racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent))

from rag.core.retrievers import DenseRetriever, SparseRetriever
from rag.neo4j_ontology_agent import Neo4jOntologyAgent

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Questions de test - une par interdiction et un pays
TEST_QUESTIONS = [
    {
        "pays": "Algérie",
        "code_pays": "alg",
        "interdiction": "Chalutage de fond",
        "question": "Est-ce qu'il existe un article portant sur l'interdiction du chalutage de fond alg ?"
    },
    {
        "pays": "Sénégal",
        "code_pays": "sen",
        "interdiction": "Chasse à la baleine",
        "question": "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines sen ?"
    },
    {
        "pays": "Maroc",
        "code_pays": "mor",
        "interdiction": "Construction côtière",
        "question": "Est-ce qu'il existe un article portant sur l'interdiction de construire sur le littoral ou au domaine public maritime mor ?"
    },
    {
        "pays": "Côte d'Ivoire",
        "code_pays": "ivc",
        "interdiction": "Extraction de sable",
        "question": "Est-ce qu'il existe un article portant sur l'interdiction de l'extraction de sable sur le littoral ivc ?"
    },
    {
        "pays": "Mauritanie",
        "code_pays": "mau",
        "interdiction": "Oiseaux Marins",
        "question": "Est-ce qu'il existe un article portant sur l'interdiction des oiseaux marins mau ?"
    },
    {
        "pays": "France",
        "code_pays": "fra",
        "interdiction": "Rejet d'hydrocarbures",
        "question": "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures fra ?"
    }
]


class QuickTester:
    """Testeur rapide du système RAG"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        if verbose:
            logger.setLevel(logging.DEBUG)
        
        self.fusion = None
        self.llm_gen = None
        self.query_analyzer = None
        self.neo4j_bridge = None
        self.graph_retriever = None
        self.ontology_agent = None
        self.dense_retriever = None
        self.sparse_retriever = None
    
    def init_system(self) -> bool:
        """Initialise les composants du système RAG"""
        try:
            print("\n📌 Initialisation du système RAG...\n")
            
            # Initialiser les retrievers classiques
            print("  1️⃣  Initialisant Dense et Sparse retrievers...", end=" ", flush=True)
            self.dense_retriever = DenseRetriever()
            self.sparse_retriever = SparseRetriever()
            print("✓")
            
            # Initialiser le pont Neo4j
            print("  2️⃣  Connectant à Neo4j...", end=" ", flush=True)
            self.neo4j_bridge = Neo4jBridge.from_config()
            if not self.neo4j_bridge.is_ready():
                print("⚠ (Bridge non prêt)")
            else:
                print("✓")
            
            # Initialiser le retriever du graph
            print("  3️⃣  Initialisant Neo4j Graph Retriever...", end=" ", flush=True)
            self.graph_retriever = Neo4jGraphRetriever(self.neo4j_bridge)
            print("✓")
            
            # Initialiser l'agent d'ontologie
            print("  4️⃣  Initialisant Neo4j Ontology Agent...", end=" ", flush=True)
            self.ontology_agent = Neo4jOntologyAgent(self.neo4j_bridge)
            print("✓")
            
            # Initialiser la fusion hybride
            print("  5️⃣  Initialisant Hybrid Fusion...", end=" ", flush=True)
            self.fusion = HybridFusion()
            print("✓")
            
            # Initialiser l'analyseur de requête
            print("  6️⃣  Initialisant Query Analyzer...", end=" ", flush=True)
            self.query_analyzer = QueryAnalyzer()
            print("✓")
            
            # Initialiser le générateur LLM
            print("  7️⃣  Initialisant LLM Generator...", end=" ", flush=True)
            self.llm_gen = LLMGenerator()
            print("✓")
            
            # Tester la disponibilité du LLM
            print("  8️⃣  Vérifiant disponibilité du LLM...", end=" ", flush=True)
            if not self.llm_gen.is_ollama_available():
                print("❌")
                print("    ⚠️  AVERTISSEMENT: LLM non disponible!")
                return False
            print("✓")
            
            print("\n✅ Système prêt!\n")
            return True
            
        except Exception as e:
            print(f"❌\n    Erreur: {e}")
            logger.error(f"Erreur lors de l'initialisation: {e}", exc_info=True)
            return False
    
    def test_question(self, q_data: dict, index: int, total: int) -> dict:
        """Teste une question"""
        question = q_data["question"]
        pays = q_data["pays"]
        interdiction = q_data["interdiction"]
        
        print(f"[{index}/{total}] {pays} - {interdiction}")
        print(f"    Question: {question[:70]}...")
        print(f"    Traitement...", end=" ", flush=True)
        
        try:
            # 1. Analyser la requête
            intent, weights, country_filter = self.query_analyzer.analyze(question)
            
            # 2. Récupérer les résultats de chaque retriever
            retriever_results = {}
            if self.dense_retriever.is_ready():
                retriever_results["dense"] = self.dense_retriever.retrieve(question, top_k=5)
            if self.sparse_retriever.is_ready():
                retriever_results["sparse"] = self.sparse_retriever.retrieve(question, top_k=5)
            if self.graph_retriever.is_ready():
                retriever_results["graph"] = self.graph_retriever.retrieve(question, top_k=5)
            
            # 3. Synonym_sets
            synonym_sets = {}
            if self.neo4j_bridge.is_ready():
                import re
                words = re.findall(r"[a-zà-ÿ]{4,}", question.lower())
                synonym_sets = self.neo4j_bridge.get_synonyms_batch(words)
            
            # 4. Fusionner
            fusion_results = self.fusion.fuse(
                retriever_results=retriever_results,
                weights=weights,
                synonym_sets=synonym_sets,
                top_k=5,
                country_filter=country_filter,
                query=question
            )
            
            # 5. Enrichir
            enriched_context = None
            if self.ontology_agent.is_ready():
                enriched_context = self.ontology_agent.enrich(question, fusion_results)
            
            # 6. Générer
            response = self.llm_gen.generate(
                query=question,
                fusion_results=fusion_results,
                intent=intent,
                enriched_context=enriched_context
            )
            
            answer = response.get("answer", "ERREUR")
            model = response.get("model", "unknown")
            
            # Afficher le résultat
            if "OUI" in answer.upper():
                result = "✅ OUI"
            elif "NON" in answer.upper():
                result = "❌ NON"
            else:
                result = "⚠️  AUTRE"
            
            print(f"{result}")
            print(f"    Modèle: {model}")
            print(f"    Réponse: {answer[:100]}...\n")
            
            return {
                "success": True,
                "pays": pays,
                "interdiction": interdiction,
                "reponse": answer[:100],
                "modele": model
            }
            
        except Exception as e:
            print(f"❌ ERREUR")
            print(f"    {str(e)[:100]}...\n")
            return {
                "success": False,
                "pays": pays,
                "interdiction": interdiction,
                "erreur": str(e)[:100]
            }
    
    def run(self):
        """Exécute le test"""
        print("\n" + "="*70)
        print("🧪 TEST RAPIDE DU SYSTÈME RAG")
        print("="*70)
        
        # Initialiser
        if not self.init_system():
            print("❌ Le système n'est pas disponible. Vérifiez:")
            print("   - Neo4j est lancé et accessible")
            print("   - Ollama est lancé OU GROQ_API_KEY est définie")
            print("   - Les modèles d'embeddings sont chargés")
            return
        
        # Exécuter les tests
        print("="*70)
        print("🚀 EXÉCUTION DES TESTS")
        print("="*70 + "\n")
        
        resultats = []
        for idx, q_data in enumerate(TEST_QUESTIONS, 1):
            result = self.test_question(q_data, idx, len(TEST_QUESTIONS))
            resultats.append(result)
        
        # Résumé
        print("="*70)
        print("📊 RÉSUMÉ DU TEST")
        print("="*70)
        
        total = len(resultats)
        success = sum(1 for r in resultats if r.get("success", False))
        errors = total - success
        
        print(f"Tests réussis: {success}/{total}")
        print(f"Erreurs: {errors}/{total}")
        
        if errors == 0:
            print("\n✅ TOUS LES TESTS RÉUSSIS!")
            print("\n💡 Prochaine étape:")
            print("   python batch_query_system.py")
        else:
            print(f"\n⚠️  {errors} test(s) échoué(s)")
            print("\n💡 Vérifiez:")
            print("   - Les modèles d'embeddings sont chargés")
            print("   - Neo4j est alimenté avec les données")
            print("   - Le LLM est correctement configuré")
        
        print("\n" + "="*70)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test rapide du système RAG"
    )
    parser.add_argument("--verbose", action="store_true", help="Mode verbose")
    
    args = parser.parse_args()
    
    tester = QuickTester(verbose=args.verbose)
    tester.run()


if __name__ == "__main__":
    main()
