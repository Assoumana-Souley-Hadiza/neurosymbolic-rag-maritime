import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

class RagasDataCollector:
    """
    Collecte les données au format attendu par RAGAS :
    - question
    - answer
    - contexts (List[str])
    - ground_truth (optionnel)
    """
    
    def __init__(self, output_dir: str = "results/eval"):
        self.output_path = Path(output_dir)
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.current_file = self.output_path / f"ragas_data_{datetime.now().strftime('%Y%m%d')}.json"
        
    def add_sample(self, question: str, answer: str, contexts: List[str], ground_truth: Optional[str] = None):
        """Ajoute un échantillon au fichier JSON."""
        sample = {
            "question": question,
            "answer": answer,
            "contexts": contexts,
            "ground_truth": ground_truth
        }
        
        data = []
        if self.current_file.exists():
            with open(self.current_file, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
        
        data.append(sample)
        
        with open(self.current_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        return self.current_file
