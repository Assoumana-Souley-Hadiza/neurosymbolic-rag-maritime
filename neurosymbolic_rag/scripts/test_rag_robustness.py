from rag.core.query_analyzer import QueryAnalyzer
from rag.core.fusion import CrossEncoderReranker
from rag.llm_generator import PromptBuilder

print("=== TEST QUERY ANALYZER ===")
qa = QueryAnalyzer()
queries = [
    "Est-ce que l'utilisation du chalutage de fond au Maroc entraîne une peine de prison ?",
    "Est-ce que le chalutage entraîne une sanction financière ?",
    "Y a-t-il une exception pour la temporalité du chalutage en France ?",
    "Quelles sont les administrations responsables du contrôle au Sénégal ?",
    "L'interdiction s'applique-t-elle à des zones spécifiques ?"
]

for q in queries:
    intent, weights, country = qa.analyze(q)
    print(f"Q: {q}")
    print(f"  -> Intent: {intent}")
    print(f"  -> Country: {country}")
    print(f"  -> Weights: {weights}")
    
print("\n=== TEST PROMPT BUILDER ===")
pb = PromptBuilder()
system, user = pb.build("Test question?", "", None, intent="sanction_penale")
print("Instruction ajoutée pour sanction_penale :")
print(user.split("Question :")[1])

print("\n=== TEST RERANKER (Init) ===")
try:
    reranker = CrossEncoderReranker()
    if reranker.model:
        docs = [{"text": "Le chalutage est puni d'une amende de 1000 euros."},
                {"text": "Le chalutage est passible de 2 ans de prison."}]
        res = reranker.rerank("Est-ce qu'il y a une peine de prison ?", docs, top_k=1)
        print("Meilleur doc trouvé :")
        print(res[0]["text"])
        print(f"Score: {res[0]['rerank_score']}")
    else:
        print("Reranker initialisé mais modèle non chargé (sentence_transformers manquant ?)")
except Exception as e:
    print(f"Erreur Reranker: {e}")
