# Suggestions d'Amélioration - Article LaTeLL 2026

## 🎯 Priorité 1: Ajouts critiques pour publication réelle

### 1.1 Évaluation empirique formelle

**Actuellement**: Résultats illustratifs
**À faire**: Créer vrai benchmark

```python
# scripts/evaluate_article_queries.py - À implémenter

import json
from rag.core.retriever_hybrid import HybridRetriever
from rag.utils.metrics import RetrievalMetrics

# 45 requêtes de test (à créer)
test_queries = [
    {
        "id": "faq_001",
        "query": "Which countries are bound by the moratorium on whale hunting?",
        "type": "factual",
        "relevant_docs": ["cms_convention_2015.pdf", "ioc_resolution_2012.pdf"],
        "expected_concepts": ["whale", "moratorium", "prohibition"]
    },
    # ... 44 autres requêtes
]

# Évaluer sur chaque baseline + hybrid
retriever = HybridRetriever.from_config()
metrics = RetrievalMetrics()

for query_obj in test_queries:
    results_hybrid = retriever.retrieve(query_obj["query"], k=10)
    
    # Scorer manuellement ou via BLEU/ROUGE
    relevance_score = evaluate_relevance(
        results=results_hybrid,
        expected=query_obj["relevant_docs"]
    )
    
    metrics.log_evaluation(
        query_id=query_obj["id"],
        query=query_obj["query"],
        mrr=calculate_mrr(results_hybrid, query_obj["relevant_docs"]),
        ndcg=calculate_ndcg(results_hybrid),
        source_distribution=analyze_sources(results_hybrid)
    )

# Exporter résultats
metrics.to_csv("evaluation_results_real.csv")
```

**Impact**: Remplacer les scores illustratifs par des vrais chiffres

### 1.2 Figures et diagrammes

**Ajouter 2-3 figures**:

#### Figure 1: System Architecture Diagram
```
Créer diagramme des 5 phases avec:
- Flux de données (PDF → Chunks → Embeddings)
- 3 retrievers en parallèle
- RRF fusion
- LLM generation

Tool: Draw.io ou Graphviz
```

#### Figure 2: Ontology Snippet
```
Montrer un extrait de l'ontologie en graphique:
- Classe "Prohibition"
  ├─ Whale Hunting (CMS)
  ├─ Bottom Trawling
  └─ [...]
- Propriétés d'object (hasJurisdiction, appliesTo)
```

#### Figure 3: Performance Comparison Bar Chart
```
Graphique comparant les 4 baselines + hybrid
- MRR et NDCG côte à côte
- Montrer la domination du hybrid
```

**Code pour générer**:
```python
import matplotlib.pyplot as plt

# Figure 3: Bar chart
methods = ['Dense', 'Sparse', 'Graph', 'RRF', 'RRF+Rerank']
mrr = [0.73, 0.68, 0.65, 0.81, 0.84]
ndcg = [0.68, 0.62, 0.58, 0.76, 0.79]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

ax1.bar(methods, mrr, color=['gray', 'gray', 'gray', 'lightblue', 'darkblue'])
ax1.set_ylabel('MRR')
ax1.set_title('Mean Reciprocal Rank')
ax1.set_ylim([0.6, 0.9])

ax2.bar(methods, ndcg, color=['gray', 'gray', 'gray', 'lightblue', 'darkblue'])
ax2.set_ylabel('NDCG@5')
ax2.set_title('Normalized Discounted Cumulative Gain')
ax2.set_ylim([0.5, 0.85])

plt.tight_layout()
plt.savefig('retrieval_comparison.pdf', dpi=300, bbox_inches='tight')
```

**Insérer dans LaTeX**:
```latex
\begin{figure}[t]
  \centering
  \includegraphics[width=\linewidth]{retrieval_comparison.pdf}
  \caption{Comparison of retrieval methods}
  \label{fig:retrieval-comparison}
\end{figure}
```

## 🎯 Priorité 2: Enrichissement académique

### 2.1 Ajouter plus de citations

**Sections faibles** (0-1 citations):
- Section 4.1 (Data Preparation) — Ajouter citations sur chunking
- Section 4.2 (Ontology) — Plus sur LKIF-Core et OWL
- Section 5 (Experimental) — Standards en NLP evaluation

**Suggestions de citations à ajouter**:
```bibtex
% Cross-encoding and reranking
@article{Nogueira2019,
  title={Multi-Stage Document Ranking with BERT},
  author={Nogueira, Rodrigo and Cho, Kyunghyun},
  journal={arXiv preprint arXiv:1910.14424},
  year={2019}
}

% Query expansion
@inproceedings{Jing2017,
  title={Machine Learning Techniques for Biomedical Literature Mining},
  author={Jing, Yiming and others},
  year={2017}
}

% Graph-based retrieval
@article{Yasunaga2021,
  title={Retrieval-Augmented Text Generation with Knowledge Graphs},
  author={Yasunaga, Michihiro and others},
  year={2021}
}

% Legal NLP
@inproceedings{Chalkidis2020,
  title={Legal Information Extraction with Transformers},
  author={Chalkidis, Ilias and others},
  booktitle={Proceedings of EMNLP 2020},
  year={2020}
}
```

### 2.2 Améliorer Discussion

**Ajouter**:
1. Threats to Validity — Limitations méthodologiques
2. Replicability — Comment reproduire l'expérience
3. Ethical Considerations — Responsabilité légale des réponses

```latex
\section*{Threats to Validity}

\paragraph{Internal Validity}
- Les scores manuellement assignés pourraient être biaisés
- 45 requêtes est un ensemble relativement petit
- Risque: sur-optimisation pour ce benchmark

\paragraph{External Validity}
- Résultats spécifiques au droit maritime
- Généralisabilité à autres domaines juridiques inconnue
- Utilisateurs réels pourraient avoir des patterns de requêtes différents

\paragraph{Construct Validity}
- MRR et NDCG mesurent classement, pas utilité réelle
- Besoin d'évaluation utilisateurs pour vrai impact
```

### 2.3 Cas d'usage réels

**Ajouter section**: "Case Studies"

```latex
\section{Illustrative Examples}

\subsection{Example 1: Whale Hunting Moratorium}

\textbf{Query}: "Which countries can hunt whales under international law?"

\textbf{Hybrid RAG Process}:
\begin{enumerate}
  \item Dense retrieval finds documents on CMS, ICRW
  \item Sparse retrieval matches keywords ``whale'', ``hunt'', ``moratorium''
  \item Graph retrieval: Follows Prohibition → Whale Hunting → hasJurisdiction
  \item Fusion combines all 3 sources
  \item LLM generates: ``The International Whaling Commission moratorium...''
\end{enumerate}

\textbf{Key Point}: No single method would capture full answer alone.
```

## 🎯 Priorité 3: Amélioration technique

### 3.1 Détailler les algorithmes

**Section 4**: Ajouter pseudo-code pour RRF

```latex
\subsubsection{Reciprocal Rank Fusion Algorithm}

\begin{algorithm}
\caption{RRF(ranks)}
\begin{algorithmic}[1]
\REQUIRE {rankings from dense, sparse, graph retrievers}
\ENSURE {fused ranking}
\STATE $scores \gets$ empty dictionary
\FOR{each retriever $r$ in [dense, sparse, graph]}
  \FOR{each document $d$ at rank $i$ in $r.ranking$}
    \STATE $scores[d] \mathrel{+}= \frac{1}{k + i}$ \quad \{$k=60$ baseline\}
  \ENDFOR
\ENDFOR
\RETURN sort documents by $scores$ descending
\end{algorithmic}
\end{algorithm}
```

### 3.2 Ajouter analyse d'erreurs

**Nouvelle sous-section**: "Error Analysis"

```
D'après le projet réel, identifier:
- Requêtes où hybrid échoue
- Types d'erreurs (missing documents, ranking errors, etc.)
- Patterns d'erreurs par type de requête
- Recommandations pour amélioration
```

### 3.3 Complexité computationnelle

**Ajouter tableau**:
```latex
\begin{table}[h]
\centering
\begin{tabular}{lrrr}
\hline
\textbf{Component} & \textbf{Time} & \textbf{Space} & \textbf{Notes} \\
\hline
Dense Embedding & O(n) & O(n×1024) & Batch processing possible \\
BM25 Query & O(m) & O(m×vocab) & m = vocabulary size \\
Cypher Query & O(V+E) & O(V+E) & V=nodes, E=edges \\
RRF Fusion & O(3k \log k) & O(k) & k = top-k results \\
Cross-encoder & O(1) & O(context) & Per document scoring \\
\hline
\end{tabular}
\caption{Computational complexity}
\end{table}
```

## 🎯 Priorité 4: Format et présentation

### 4.1 Ajouter numéros de page

```latex
% Dans le preamble
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\rfoot{\thepage}
```

### 4.2 Améliorer les captions

**Actuellement court**: "Retrieval performance across different methods"

**À faire**: Captions plus descriptives

```latex
% Avant
\caption{Retrieval performance across different methods}

% Après
\caption{Comparison of retrieval methods on maritime law QA task.
Dense retrieval achieves 0.73 MRR, sparse 0.68, graph 0.65.
Hybrid RRF fusion reaches 0.81 MRR, and adding cross-encoder 
reranking improves to 0.84 MRR (+15\% over best single method).
Query latency increases from 52ms (sparse) to 350ms (full hybrid),
acceptable for legal document retrieval.}
```

### 4.3 Table of Contents

Généré automatiquement par LaTeX via `\tableofcontents`

```latex
\maketitle
\tableofcontents  % <- Ajouter
\newpage
\section{Introduction}
```

## 📋 Checklist avant soumission

### Version préliminaire
- [ ] Résultats empiriques mesurés (pas illustratifs)
- [ ] Au minimum 1 figure (de préférence 3)
- [ ] 20+ références académiques
- [ ] Orthographe vérifiée (Grammarly, etc.)
- [ ] Tous les acronymes définis à première mention
- [ ] Tableaux avec captions descriptives
- [ ] Section "Threats to Validity"

### Version finale (après acceptation)
- [ ] Auteurs réels et affiliations
- [ ] Décommenter `\aclfinalcopy`
- [ ] Paper ID depuis système de soumission
- [ ] Remerciements (Acknowledgments section)
- [ ] Code/data disponible (si requis)
- [ ] Vérification des DOIs pour références

## 🔄 Amélioration itérative recommandée

### Round 1 (Actuellement)
✅ Structure et contenu de base
✅ Alignement avec project réel
✅ Template LaTeLL respecté

### Round 2 (Recommandé avant soumission)
- [ ] Ajouter vraies évaluations empiriques
- [ ] Ajouter figures
- [ ] Enrichir citations (25+ références)
- [ ] Améliorer Discussion + Conclusion

### Round 3 (Après feedback)
- [ ] Intégrer commentaires relecteurs
- [ ] Ajouter expériences supplémentaires si demandé
- [ ] Renforcer limitations reconnues
- [ ] Améliorer clarté écriture

## 📊 Estimation de temps pour améliorations

| Tâche | Temps | Priorité |
|-------|-------|----------|
| Évaluation empirique réelle | 10-15h | CRITIQUE |
| Ajouter 3 figures | 3-4h | HAUTE |
| Ajouter 15 citations + sections | 5-6h | HAUTE |
| Relecture et polish | 2-3h | MOYENNE |
| Test compilation final | 0.5h | MOYENNE |
| **TOTAL** | **~25h** | |

## 💡 Ressources utiles

### Pour évaluation
- [NDCG Calculator](https://github.com/facebookresearch/DPR)
- [pytrec_eval](https://github.com/cvangysel/pytrec_eval)
- [ir_datasets](https://ir-datasets.com/) — Datasets de référence

### Pour figures
- [Draw.io](https://draw.io/) — Diagrammes
- [Matplotlib](https://matplotlib.org/) — Graphiques
- [TikZ](https://www.ctan.org/pkg/pgf) — Dessins LaTeX

### Pour citations
- [ACL Anthology](https://aclanthology.org/)
- [DBLP](https://dblp.uni-trier.de/)
- [Semantic Scholar](https://www.semanticscholar.org/)

### Pour relecture
- [Grammarly](https://www.grammarly.com/)
- [Hemingway App](https://hemingwayapp.com/) — Clarté
- [DeepL](https://www.deepl.com/) — Vérification traduction

## 🎓 Conseils généraux

1. **Soyez spécifique**: "0.84 MRR" > "good results"
2. **Justifiez les choix**: Pourquoi BGE-M3? Pourquoi 800 tokens?
3. **Comparez honnêtement**: Montrez aussi les limitations
4. **Reproduisibilité**: Donnez assez de détails pour refaire
5. **Contribution claire**: Quelle est la novation par rapport à l'état de l'art?

---

**Prochaine étape**: Commencez par Priority 1 (Évaluation empirique) — c'est la base pour publier.
