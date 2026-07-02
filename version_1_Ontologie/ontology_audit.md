# 🔍 Audit Expert — Ontologie Maritime Juridique

## Niveau Actuel : 6/10 — "Bon squelette, mais le sang ne circule pas encore"

Ton ontologie a un **excellent cadre théorique** (T-Box), mais elle souffre d'un problème fondamental : **les données extraites de tes documents ne sont pas réellement injectées comme relations dans le graphe**. Elles flottent comme des étiquettes isolées.

---

## ✅ Ce qui est BIEN fait (Forces)

### 1. Architecture T-Box exemplaire (`schema.py` — 937 lignes)
- **114 classes OWL** bien organisées en 11 axes thématiques (Norme, Zone, Activité, Acteur, Espèce, Source, Période, Exception, Contrôle, Sanction, Stock)
- Alignement **LKIF-Core** rigoureux (Norm → Prohibition/Permission/Obligation)
- Intégration **OWL-Time** pour la modélisation temporelle
- **Axiomes OWL 2 DL** correctement formulés :
  - Restrictions existentielles (`someValuesFrom`) : toute Interdiction DOIT avoir au moins 1 Zone, 1 Activité, 1 Acteur, 1 Source
  - Restrictions universelles (`allValuesFrom`) : la chasse commerciale n'affecte QUE les cétacés
  - Classes équivalentes pour raisonnement automatique (`ZoneInterdite`, `ActiviteIllicite`, `ActeurEnInfraction`)
  - Chaîne de propriétés : `pratiqueActivite ∘ estActiviteDe → estSoumisA`
- **Disjonctions complètes** entre types déontiques, types d'activités, types d'acteurs

### 2. Populator structuré (`populator.py` — 1118 lignes)
- Les 6 interdictions (I001-I006) sont codées manuellement avec traçabilité complète
- Chaque interdiction a : Zone, Acteur, Source, Exception, Contrôle, Sanction, Période
- 25 espèces marines avec noms scientifiques latins
- 17 sources juridiques avec années et définitions SKOS bilingues (fr/en)
- Couche lexicale SKOS avec 16 concepts techniques (ICRW, MARPOL, CDB)

### 3. Métadonnées de qualité
- Labels bilingues (fr/en) sur toutes les classes et propriétés
- `skos:definition` sur la grande majorité des ressources
- Namespace propre (`http://www.maritime-ontology.org/mar#`)
- En-tête ontologique avec licence CC-BY-4.0, versioning, imports

---

## ❌ Problèmes CRITIQUES identifiés

### 🔴 PROBLÈME 1 : Les triplets extraits par Mistral ne deviennent PAS des relations dans le graphe

C'est **le problème le plus grave**. Tes fichiers JSON (`I001_Chalutage_de_fond_final.json`, etc.) contiennent des triplets très riches extraits par l'IA :

```json
{
  "subject": "I001",
  "predicate": "mar:appliesInZone",
  "object": "mar:Zone_HAUTE_MER",
  "confidence": 0.99
}
```

**Mais `loader.py` ne les transforme PAS en vrais triplets RDF !**

En examinant le code, voici ce qui se passe réellement :
1. `loader.py` charge les JSON et extrait les `pipeline_triples` → ✅ OK
2. `loader.py` extrait les `entites_trouvees` et les transforme en **définitions textuelles** → ❌ Problème
3. `populator.py` reçoit ces données mais ne les utilise que pour créer des `ConceptLexical` (SKOS) → ❌ Problème

**Résultat** : Tes 30+ triplets par interdiction (soit ~180 relations extraites) sont **ignorés**. Seules les relations codées à la main dans `populator.py` existent (les ~137 que tu vois dans Neo4j).

> [!CAUTION]
> L'IA a extrait des données précieuses (zones spécifiques, acteurs détaillés, sanctions avec références d'articles) mais elles sont converties en simples étiquettes textuelles au lieu d'être injectées comme des arêtes du graphe.

### 🔴 PROBLÈME 2 : Les entités extraites deviennent des "ConceptLexical" flottants

Dans le TTL de sortie, on voit des centaines de nœuds comme :

```turtle
mar:Concept_chalutage_de_fond_bottom_trawling_en_haute_mer_sans_evaluati
    a mar:ConceptLexical, skos:Concept ;
    skos:definition "Entité de type 'Activity' — chalutage de fond..." ;
    skos:prefLabel "chalutage de fond (bottom trawling)..." .
```

Ce nœud **sait** qu'il est une "Activity" (c'est écrit dans sa définition textuelle), mais il n'est **PAS typé** comme `mar:ChalutageFond`. Il n'a **aucune relation** vers `I001`. C'est un nœud flottant dans le graphe.

**Sur tes 551 nœuds, environ 400 sont des ConceptLexical isolés** qui ne participent à aucun raisonnement.

### 🔴 PROBLÈME 3 : Les `Definitions_retenues` (757 ko de données) sont sous-exploitées

Le dossier `Definitions_retenues/` contient 6 fichiers JSON massifs (757 ko total) avec des définitions très détaillées extraites des vrais documents. Elles sont bien chargées par `load_definitions_retenues()` et injectées comme `skos:Concept`, mais :
- Elles ne sont **pas liées aux interdictions** correspondantes (pas de `mar:hasConcept I001 → Def_I001_xxx`)
- Elles ne sont **pas liées entre elles** (pas de `skos:broader`, `skos:related`)
- Elles n'ont **pas de type OWL** (une définition de "Zone Spéciale MARPOL" n'est pas typée comme `mar:ZoneSpecialeMARPOL`)

### 🟡 PROBLÈME 4 : Le raisonnement OWL est désactivé → les axiomes sont décoratifs

Tu as de magnifiques axiomes dans `schema.py` :
- `ZoneInterdite ≡ Zone ⊓ ∃estZoneDe.Interdiction`
- `ActeurEnInfraction ≡ Acteur ⊓ ∃pratiqueActivite.ActiviteIllicite`
- Chaîne : `pratiqueActivite ∘ estActiviteDe → estSoumisA`

Mais avec `--no-reason`, ces axiomes **ne produisent aucune inférence**. Ils ne sont que du texte mort dans le fichier OWL. Et Neo4j ne comprend pas du tout les axiomes OWL.

### 🟡 PROBLÈME 5 : La couverture GraphRAG est insuffisante

Pour qu'un RAG puisse répondre à *"Un chalutier peut-il pêcher dans un EMV ?"*, il faut que le graphe contienne des chemins navigables. Actuellement :
- `I001 → appliesInZone → ZEV` ✅ (codé main)
- `I001 → concerneActivite → Activite_CHALUTAGE_FOND` ✅ (codé main)
- Mais les **détails fins** (articles précis, conditions, seuils) sont enfermés dans du texte, pas dans des relations

---

## 📋 Plan d'Amélioration — 4 Phases

### Phase 1 : Injecter les triplets extraits comme VRAIES relations RDF
**Fichier à modifier** : `populator.py` ou nouveau fichier `triple_injector.py`

Pour chaque triplet dans `pipeline_triples` :
1. Résoudre le `subject` → URI existant (ex: `I001` → `mar:I001`)
2. Résoudre le `predicate` → propriété OWL existante (ex: `mar:appliesInZone`)
3. Résoudre ou **créer** le `object` → individu typé (ex: `mar:Zone_HAUTE_MER` → créer si n'existe pas, avec le bon type `mar:ZoneHauteMer`)
4. Ajouter le triplet RDF au graphe
5. Conserver le `confidence` comme data property

**Impact** : Passer de ~137 relations à ~300+ relations réelles dans Neo4j.

### Phase 2 : Typer les entités extraites au lieu de les mettre en ConceptLexical

Quand Mistral extrait une entité avec `categorie: "Zone"`, il faut créer un individu de type `mar:Zone`, pas un `mar:ConceptLexical`.

Mapping proposé :
| Catégorie Mistral | Classe OWL |
|---|---|
| `Activity` | `mar:Activite` (ou sous-classe) |
| `Zone` | `mar:Zone` (ou sous-classe) |
| `Actor` | `mar:Acteur` (ou sous-classe) |
| `Sanction` | `mar:Sanction` |
| `Controle` | `mar:Controle` |
| `Exception` | `mar:ExceptionJuridique` |
| `Espece` | `mar:EspeceMarine` |
| `Periode` | `mar:Periode` |

### Phase 3 : Matérialiser les inférences clés directement dans Neo4j

Puisque Neo4j ne fait pas de raisonnement OWL, il faut **pré-calculer** les classes inférées :
- Tout nœud `Zone` qui est relié à une `Interdiction` via `estZoneDe` → ajouter le label `ZoneInterdite`
- Tout nœud `Activité` reliée à une `Interdiction` → ajouter le label `ActiviteIllicite`
- Résoudre la chaîne `pratiqueActivite ∘ estActiviteDe` et créer explicitement les liens `estSoumisA`

### Phase 4 : Lier les définitions retenues au graphe

Pour chaque définition dans `Definitions_retenues/` :
1. Créer un lien `mar:hasConcept` entre l'interdiction et le concept
2. Utiliser `skos:broader` / `skos:narrower` pour structurer le glossaire
3. Si possible, détecter automatiquement le type OWL (Zone, Acteur, etc.) à partir du champ `document_title` ou du contenu

---

## 🎯 Bonnes Pratiques de Construction d'Ontologie (Checklist)

| Pratique | État actuel | Action |
|---|---|---|
| Noms de classes en CamelCase | ✅ OK | — |
| Labels bilingues (fr/en) | ✅ OK | — |
| Disjonctions entre classes sœurs | ✅ OK | — |
| Domaine/Range sur toutes les propriétés | ✅ OK | — |
| `owl:imports` des ontologies alignées | ✅ OK (LKIF, OWL-Time) | — |
| Pas de "punning" (classe = individu) | ✅ OK | — |
| Toute donnée vient des sources | ⚠️ Partiel | Phase 1 |
| Pas de nœuds orphelins | ❌ ~400 nœuds flottants | Phase 2 |
| Axiomes produisent des inférences | ❌ Désactivé | Phase 3 |
| Glossaire lié au graphe | ❌ Isolé | Phase 4 |
| IRI stables et lisibles | ⚠️ IRIs tronqués pour les Concepts | Nettoyer |
| Validation par un raisonneur (HermiT/Pellet) | ❌ Non fait | Tester avec Protégé |

---

## 🏆 Résumé

> **Le squelette (T-Box) est de niveau recherche.** L'architecture axiomatique avec LKIF-Core, les restrictions OWL 2 DL, et les classes équivalentes sont du travail de qualité universitaire.

> **Le sang (A-Box) ne circule pas encore.** Les données extraites par Mistral sont stockées comme du texte plat au lieu d'être injectées comme des relations navigables. C'est LA priorité #1 pour que ton GraphRAG fonctionne.

**Si tu appliques la Phase 1 (injection des triplets)**, tu passeras de 137 à 300+ relations, et ton graphe deviendra immédiatement exploitable par un RAG. C'est l'amélioration avec le meilleur rapport effort/impact.
