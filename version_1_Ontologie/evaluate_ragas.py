import os
import json
from pathlib import Path
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevance,
    context_precision,
    context_recall
)
from langchain_groq import ChatGroq

def run_evaluation(json_file: str):
    """Lance l'évaluation RAGAS sur un fichier JSON produit par le collecteur."""
    
    if not os.path.exists(json_file):
        print(f"Erreur : Le fichier {json_file} n'existe pas.")
        return

    # 1. Charger les données
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # RAGAS attend des listes pour chaque colonne
    dataset_dict = {
        "question": [item["question"] for item in data],
        "answer": [item["answer"] for item in data],
        "contexts": [item["contexts"] for item in data],
        # Ground truth est souvent absent au début, RAGAS peut quand même calculer 
        # la fidélité et la pertinence de la réponse.
    }
    
    # Ajouter ground_truth si présent
    if all("ground_truth" in item and item["ground_truth"] for item in data):
        dataset_dict["ground_truth"] = [item["ground_truth"] for item in data]

    dataset = Dataset.from_dict(dataset_dict)

    # 2. Configurer le LLM de critique (Groq Llama 3)
    # RAGAS a besoin d'un LLM pour noter les réponses
    llm = ChatGroq(
        temperature=0,
        model_name="llama-3.3-70b-versatile",
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

    # 3. Exécuter l'évaluation
    print(f"🚀 Lancement de l'évaluation sur {len(data)} échantillons...")
    
    # On utilise le LLM Groq pour l'évaluation
    result = evaluate(
        dataset,
        metrics=[
            faithfulness,
            answer_relevance,
            context_precision
        ],
        llm=llm
    )

    # 4. Afficher et sauvegarder les résultats
    df = result.to_pandas()
    output_csv = json_file.replace(".json", "_scores.csv")
    df.to_csv(output_csv, index=False)
    
    print("\n✅ Évaluation terminée !")
    print(f"📊 Résultats sauvegardés dans : {output_csv}")
    print("\nScores moyens :")
    print(df.mean(numeric_only=True))

if __name__ == "__main__":
    # Trouver le fichier le plus récent dans results/eval
    eval_dir = Path("results/eval")
    files = list(eval_dir.glob("ragas_data_*.json"))
    
    if not files:
        print("Aucune donnée collectée. Utilisez l'application Streamlit d'abord.")
    else:
        latest_file = max(files, key=os.path.getctime)
        run_evaluation(str(latest_file))
