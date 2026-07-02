# 📊 Analyse du Benchmark RAG Maritime — 17 mai 2026

## 1. Résultats Bruts

| Méthode | MRR | NDCG@5 | Recall@5 | P@5 | Latence |
|---|---|---|---|---|---|
| Dense only | 0.323 | 0.343 | 0.295 | 0.293 | 373ms |
| Sparse only | 0.200 | 0.200 | 0.200 | 0.193 | 92ms |
| Graph only | 0.427 | 0.404 | 0.249 | 0.240 | 206ms |
| Hybrid RRF | 0.434 | 0.475 | 0.335 | 0.360 | 503ms |
| **Hybrid + Rerank** | **0.572** | **0.571** | **0.390** | **0.453** | 3422ms |
| **Full pipeline** | **0.567** | **0.564** | **0.385** | **0.440** | 4481ms |

## 2. Interprétation — Ce qui va bien ✅

### La progression de l'ablation est très claire
Le tableau montre une progression logique et démontrable :
- **Sparse seul (0.20)** → la recherche par mots-clés bruts est faible car les textes juridiques n'utilisent pas le même vocabulaire que les questions.
- **Dense seul (0.32)** → le modèle d'embeddings (bge-m3) capte mieux le sens sémantique.
- **Graph seul (0.43)** → l'ontologie Neo4j retrouve des articles que le Dense rate complètement (ex: Q05 Maroc amendes, Q06 Mauritanie chalutage, Q10 Gabon prison).
- **Hybrid RRF (0.43)** → la fusion des 3 sources améliore le Recall mais le MRR reste similaire.
- **Hybrid + Rerank (0.57)** → le Cross-Encoder booste le classement des documents pertinents de +32% vs Hybrid seul.

> [!TIP]
> **Pour l'article** : La progression Dense (0.32) → Graph (0.43) → Hybrid+Rerank (0.57) est un excellent argument : chaque composant ajoute de la valeur.

## 3. Problèmes identifiés 🔴

### Problème 1 : Les questions PIÈGE écrasent les moyennes

Tu as **6 questions PIÈGE** (Q04, Q09, Q14, Q19, Q24, Q29) avec `relevant_keywords: []`.
La fonction `is_relevant()` exige au minimum 1 keyword trouvé (`max(1, len*0.5)`), donc pour ces questions **MRR = 0.0 par construction**, peu importe ce que le système fait.

**Impact** : Ces 6 questions (20% du dataset) tirent TOUTES les moyennes vers le bas de manière artificielle. Sans elles, le MRR du Full pipeline serait autour de **0.71** au lieu de 0.57.

### Problème 2 : 5 questions non-piège échouent dans TOUTES les configs

| Question | Pays | Thème | MRR (Full) | Cause probable |
|---|---|---|---|---|
| Q17 | Sénégal | Construction littoral | 0.0 | Keyword "côtier" absent des docs (ils disent "littoral" ou "domaine maritime") |
| Q21 | Gabon | Pêche AMP | 0.0 | Keyword "protégée" absent des docs (ils disent "parc national" ou "réserve") |
| Q23 | RDC | Prison pêche AMP | 0.0 | Keyword "emprisonnement" absent (la loi dit "peine privative de liberté" ?) |
| Q25 | Tunisie | Amendes pêche AMP | 0.0 | Keyword "amende" absent (la loi dit "sanction pécuniaire" ?) |
| Q28 | Bénin | Espèces temporalité | 0.0 | Keyword "période" absent des docs sur les espèces au Bénin |

> [!WARNING]
> **Cause racine** : les `relevant_keywords` ne correspondent pas au vocabulaire EXACT des PDF juridiques. C'est un problème d'évaluation, pas de retrieval !

### Problème 3 : Full pipeline ≈ Hybrid+Rerank

Le Full pipeline (0.567) est légèrement INFÉRIEUR au Hybrid+Rerank (0.572). L'ontologie n'apporte pas d'amélioration nette en moyenne. Détail :
- **L'ontologie AIDE** : Q02 (Sénégal baleines) passe de MRR=0.5 → 1.0 grâce aux synonymes
- **L'ontologie NUIT** : Q08 (Tunisie chalutage) passe de MRR=1.0 → 0.5 (l'expansion de requête dilue les résultats)

## 4. Plan d'action pour améliorer les résultats

### Action 1 — Séparer les questions PIÈGE dans le benchmark
Les questions PIÈGE testent un comportement DIFFÉRENT (capacité à NE PAS halluciner).
Elles doivent être évaluées avec une métrique séparée : le **Taux de Vrais Négatifs**.

### Action 2 — Corriger les relevant_keywords
Il faut vérifier dans les PDF réels quels mots exacts sont utilisés, puis mettre à jour les keywords.

### Action 3 — Augmenter le nombre de questions
30 questions c'est le **minimum absolu** pour un article. Avec tes 11 axes × 6 thèmes, tu pourrais avoir **66 questions** (en variant les pays). C'est ce que les reviewers attendent.

### Action 4 — Corriger le benchmark pour les questions NON_CADRE
Actuellement, une question NON_CADRE avec `relevant_keywords: []` donne MRR=0 automatiquement.
Il faudrait plutôt mesurer : "le système n'a-t-il trouvé AUCUN document pertinent ?" → si oui, score=1 (succès).
