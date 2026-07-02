# 🎤 PIPELINE SPEECH — Présentation Orale du Pipeline Maritime

**Durée** : 30-45 minutes  
**Audience** : Experts juridiques, data scientists, décideurs  
**Format** : Discours + démonstration des sorties

---

## 📢 Ouverture (2-3 min)

Bonjour à tous. Aujourd'hui, je vous présente un système qu'on a développé pour transformer les conventions et résolutions internationales sur le droit maritime en une **ontologie RDF/OWL structurée**.

Pour vous donner un contexte : actuellement, quand vous avez une question sur l'interdiction du chalutage de fond en haute mer, vous devez :
1. Fouiller dans 4-5 résolutions ONU différentes
2. Croiser avec les exceptions pour les États en développement
3. Vérifier les zones d'application

Avec notre système, tout ça devient **requêtable automatiquement par machine**. C'est pour ça qu'on l'appelle un **pipeline**.

---

## 🎯 Problème à résoudre (2 min)

Imaginons que vous êtes un agent de pêche qui a une question simple :

> "Je pêche en Haute Mer. Le chalutage de fond est interdit, oui ou non ?"

Bonne question. La réponse « classique » serait :

> "Techniquement, c'est interdit depuis 2006 par la Résolution AG/ONU 61/105, SAUF si tu es un État en développement avec des besoins particuliers... mais même là, il faut avoir une évaluation scientifique... ET tu dois mettre en place des mesures de conservation..."

**Trop compliqué.** 

Notre pipeline résout ça en créant une **ontologie** — litteralement, un modèle informatique du « comment les choses sont » selon le droit international maritime.

---

## 💡 Qu'est-ce qu'une ontologie ? (3 min)

Une ontologie, c'est essentiellement une **réponse structurée à la question : "Comment représenter la connaissance ?"**

Prenez le mot « Interdiction ». Une interdiction c'est quoi exactement ?

**Une représentation classique** :
```
Interdiction = String("Interdiction du chalutage de fond")
```

C'est un texte. C'est tout. Aucune structure.

**Une représentation ontologique** :
```
Interdiction {
  label: "Interdiction du Chalutage de Fond"
  appliesInZone: [Haute Mer, Écosystème Vulnérable]
  concerneActeur: [État du Pavillon, ORGP]
  aException: [Exception_EtatsDeveloppement, Exception_MesuresConservation]
  fondeeSur: [Résolution 61/105, Résolution 64/72, ...]
  protegeEspece: [Poisson démérsal, Crabe royal]
}
```

Maintenant, ce n'est plus juste un texte. C'est une **entité semantique** avec relations, properties, exceptions. Une machine peut naviguer là-dedans.

---

## 🏗️ Architecture du système (5 min)

Regardons comment on construit cette ontologie. Il y a 8 étapes, qu'on peut regrouper en 3 phases :

### Phase 1 : FONDATION (Étapes 1-2)

**Étape 1 : Import LKIF-Core**

LKIF-Core, c'est une ontologie juridique standard développée en Europe pour représenter les normes. Elle définit des concepts comme :
- Norm (une règle générale)
- Prohibition (interdit)
- Permission (autorisé)
- Exception (cas où ça ne s'applique pas)

On charge ça dans le graphe comme fondation. C'est comme avoir les **bases du droit** avant de les spécialiser au maritime.

**Étape 2 : Construction du schéma OWL**

Maintenant qu'on a les fondations juridiques, on construit notre **schéma spécifique maritime**.

Qu'est-ce qu'on crée ?

**Classes** (catégories) :
- Interdiction, Permission, Obligation (types de normes)
- Zone (Haute Mer, ZEE, Territoriale, Sanctuaire, Écosystème Vulnérable)
- Acteur (États du pavillon, ONG, Navires-usines)
- Activité (Chalutage, Chasse baleinière, Pêche électrique)
- Espèce marine (baleines, poissons démersaux)

**Propriétés** (relations entre ces classes) :
- appliesInZone : relie une interdiction à une zone
- concerneActeur : relie une interdiction aux acteurs affectés
- aException : relie une interdiction à ses exceptions
- fondeeSur : relie une interdiction à sa source juridique
- confidence : degré de confiance (0.0 à 1.0)

Après cette étape, on a la **structure vide** mais complète. C'est comme avoir les murs d'une maison avant de la meubler.

### Phase 2 : REMPLISSAGE (Étapes 3-4)

**Étape 3 : Chargement des données brutes**

Nos données brutes viennent de LLMs qui ont **extrait des conventions PDF** :
- 24 définitions clés (e.g., "toothed whale")
- 103 termes du glossaire (engins de pêche, organisations)
- 55 triplets sémantiques (relations subject-predicate-object)

Ces données sont en JSON. On les parse et on les charge en mémoire.

**Étape 4 : Population des individus**

C'est là qu'on **crée les instances** — les choses réelles.

Sous-étape 4.1 : On crée 5 zones statiques
```
HM (Haute Mer)
EEZ (Zone Économique Exclusive)
MT (Mer Territoriale)
SM (Sanctuaire Marin)
ZEV (Écosystème Vulnérable)
```

Sous-étape 4.2 : On crée les sources juridiques
Pour chaque interdiction, s'il y a des documents mentionnés (Résolutions ONU, Conventions), on crée un individu pour chacun.

Sous-étape 4.3 : **Les 8 interdictions**
- I001 : Chalutage de fond (COMPLÉTÉE) — fondée sur 4 résolutions, 3 acteurs, 2 exceptions
- I002 : Chasse baleinière (COMPLÉTÉE) — fondée sur ICRW, 4 espèces protégées
- I003-I008 : Templates vides (PAS ENCORE REMPLIES) — prêtes pour vos données futures

Sous-étape 4.4 : On intègre les triplets IA
Les 55 relations extraites du texte vont dans le graphe.

Sous-étape 4.5 : Couche lexicale SKOS
Les 127 termes/définitions du glossaire sont indexés comme concepts SKOS, avec labels et définitions multilingues (FR/EN).

Après cette phase, on a une **ontologie peuplée** — pas vide, avec contenu réel.

### Phase 3 : SORTIES ET VALIDATION (Étapes 5-8)

**Étape 5 : Export multi-format**

Maintenant qu'on a l'ontologie, on l'exporte dans 4 formats différents :

1. **Turtle (TTL)** — Format le plus **lisible par humains**. Les développeurs aiment ça.
   ```turtle
   mar:InterdictionChalutagedefond
     a mar:Interdiction ;
     rdfs:label "Interdiction du Chalutage de Fond"@fr ;
     mar:appliesInZone mar:HM .
   ```

2. **OWL/RDF-XML** — Format **standard** pour les éditeurs ontologiques comme Protégé. C'est le format « officiel ».

3. **JSON-LD** — Format **Web/API**. Si vous avez un backend JavaScript ou une REST API, c'est celui-là qu'il vous faut.

4. **N-Triples** — Format **ultra-simple** : une ligne = un triplet RDF. C'est pour le streaming et l'échange brut de données.

**Étape 6 : Questions de compétence SPARQL**

On pose 12 questions à l'ontologie pour vérifier qu'elle fonctionne :

| Question | Utilité |
|----------|---------|
| "Lister toutes les interdictions" | Vérifier qu'on a bien 8 |
| "Quels acteurs sont concernés par I001 ?" | Vérifier les relations |
| "Dans quelles zones s'applique I002 ?" | Vérifier la géographie |
| "Quelles exceptions à I001 ?" | Vérifier les déraillements |
| "Lister tous les concepts SKOS" | Vérifier le glossaire |
| "Hiérarchie des classes" | Vérifier la taxonomie |
| "Sources juridiques pour I002" | Vérifier les références |
| "Interdictions par zone" | Requête inverse |
| ... |

Si ces 12 questions obtiennent des réponses correctes, l'ontologie est **valide**.

Résultat après cette étape : **sparql_results.json** — un fichier JSON avec tous les résultats.

**Étape 7 : Export Neo4j**

On convertit l'ontologie RDF en un format que Neo4j peut importer :
```cypher
CREATE (n:Interdiction {label: "Chalutage de Fond"})
CREATE (z:Zone {label: "Haute Mer"})
CREATE (n)-[:APPLIES_IN_ZONE]->(z)
```

Ça permet de visualiser l'ontologie sous forme de graphe interactif dans Neo4j Browser.

**Étape 8 : Rapport final**

Un fichier JSON qui résume tout :
```json
{
  "total_triples": 1022,
  "classes": 57,
  "individuals": 111,
  "confidence_i001": 1.0,
  "confidence_i002": 1.0,
  "timestamp": "2026-04-14T16:45:41"
}
```

---

## 📊 Résultats concrets (3 min)

Après avoir exécuté l'ensemble du pipeline, voici ce qu'on obtient :

**Les chiffres**:
- 1022 triplets RDF
- 57 classes OWL
- 20 propriétés objet
- 11 propriétés de données
- 111 individus

**Les fichiers generés** :
- maritime_ontology.ttl (~1400 lignes)
- maritime_ontology.owl (~1600 lignes)
- maritime_ontology.jsonld (~1500 lignes)
- maritime_ontology.nt (~1450 lignes)
- neo4j_import.cypher (~250 lignes)
- sparql_results.json (12 requêtes)

**État des interdictions** :
| ID | Label | Couverture | Prête pour RAG |
|----|-------|-----------|--------------|
| I001 | Chalutage de fond | 100% | ✅ |
| I002 | Chasse baleine | 100% | ✅ |
| I003-I008 | [Templates] | 0% | ⏳ (prêts pour vos données) |

---

## 🤖 Intégration RAG (5 min)

Maintenant la vraie magie : **comment ça s'utilise dans un système RAG ?**

RAG = **Retrieval-Augmented Generation**. C'est quand vous prenez un LLM (ChatGPT, Llama, etc.) et vous l'augmentez avec une source de vérité externe — dans notre cas, l'ontologie maritime.

**Voici le flux** :

1. **Utilisateur pose une question** :
   > "Quelles sont les zones affectées par l'interdiction du chalutage de fond ?"

2. **Système convertit automatiquement en SPARQL** :
   ```sparql
   SELECT ?zone WHERE {
     mar:InterdictionChalutagedefond mar:appliesInZone ?zone .
     ?zone rdfs:label ?label .
   }
   ```

3. **Exécution sur l'index SPARQL** (Fuseki ou OWLIM)
   ```
   Résultat :
   - Haute Mer
   - Écosystème Marin Vulnérable
   ```

4. **Contexte augmenté** :
   ```
   Faits du graphe :
   - Interdiction: Chalutage de Fond (depuis 2006)
   - Zones: Haute Mer, Écosystème Vulnérable
   - Exceptions: États en développement, Mesures conservation
   - Sources: Résolution 61/105, 64/72, 66/68, 71/123
   
   Question utilisateur: Quelles zones affectées ?
   ```

5. **LLM génère réponse augmentée** :
   > "L'interdiction du chalutage de fond s'applique dans deux zones aquatiques principales selon l'ontologie maritime :
   >
   > 1. **Haute Mer** — Zone au-delà de la juridiction nationale (au-delà de 200 milles marins)
   > 2. **Zones d'Écosystème Marin Vulnérable** — Zones avec coraux froids, monts sous-marins
   >
   > Cette interdiction découle des Résolutions AG-ONU 61/105 (2006), 64/72 (2009), etc."

**Avantage** : La réponse n'est pas inventée. Elle est **grounding dans le graphe sémantique**.

---

## 🔄 Flux d'exécution (2 min)

Montrons rapidement comment c'est orchestré.

```
python main.py
  ↓
Charge data/config/interdictions.yaml
  ↓
Charge data/config/settings.yaml
  ↓
Crée un graphe RDF vide
  ↓
STEP_1: Parse data/input/lkif_stub.ttl
  ↓
STEP_2: Construit 57 classes OWL
  ↓
STEP_3: Charge data/raw/*.json (24 + 103 + 55 items)
  ↓
STEP_4: Peuple avec 8 interdictions + zones + acteurs + glossaire
  ↓
STEP_5: Export 4 formats (TTL, OWL, JSON-LD, NT)
  ↓
STEP_6: Exécute 12 requêtes SPARQL de validation
  ↓
STEP_7: Génère script Neo4j (cypher)
  ↓
STEP_8: Génère rapport JSON
  ↓
DONE: ontology_report.json
```

Durée totale : **~20-30 secondes** (sur laptop standard).

---

## 🎨 Visualisation (3 min)

Parlons de comment ça se visualise.

**Option 1 : Protégé (Éditeur ontologie)**

Vous ouvrez maritime_ontology.owl dans Protégé (application gratuite). Vous verrez :
- Arborescence des classes à gauche
- Propriétés et restrictions au centre
- Individus listés à droite

Vous pouvez cliquer sur "Interdiction" et voir ses sous-classes, ses instances, etc.

**Option 2 : Neo4j Browser**

Vous exécutez le script cypher qu'on a généré. Neo4j crée un graphe visuel :

```
(I001)-[APPLIES_IN_ZONE]->(HM)
    |
    +-[APPLIES_IN_ZONE]->(ZEV)
    |
    +-[CONCERNE_ACTEUR]->(EtatPavillon)
    |
    +-[A_EXCEPTION]->(ExceptionEtatsDeveloppement)
```

Vous pouvez naviguer, zoomer, cliquer sur les nœuds pour voir les propriétés.

**Option 3 : SPARQL Endpoint (pour RAG)**

Vous mettez l'ontologie sur un serveur SPARQL publique (Apache Jena Fuseki, Virtuoso, etc.). Les applications externes peuvent faire des requêtes :

```
GET /sparql?query=SELECT %20*%20WHERE%20...
```

---

## 📈 Cas d'usage : Vous avez besoin de... (3 min)

Montrons comment le pipeline aide dans différents scenarios :

### Cas 1 : Vous êtes juriste maritime

Vous avez besoin de **comparer les exceptions** entre I001 et I002.

**Avant le pipeline** :
- Ouvrir Résolution 61/105 (PDF)
- Chercher « exceptions »
- Ouvrir ICRW Convention (PDF)
- Chercher « exceptions »
- ...comparer manuellement

**Avec le pipeline** :
```sparql
SELECT ?interdiction ?exception WHERE {
  ?interdiction rdf:type mar:Interdiction .
  ?interdiction mar:aException ?exception .
}
ORDER BY ?interdiction
```
**Résultat** : Tableau avec toutes les exceptions, côte à côte. 10 secondes.

### Cas 2 : Vous êtes régulateur de pêche

Vous avez une demande d'État : "On peut pêcher dans cette zone ?"

**Avant le pipeline** :
- Chercher la zone sur une carte
- Croiser avec les interdictions correspondantes
- Vérifier exceptions
- ...process lent et error-prone

**Avec le pipeline** :
```sparql
SELECT ?interdiction WHERE {
  ?interdiction mar:appliesInZone mar:ZEV .
}
```
**Résultat** : Quelles interdictions s'appliquent immédiatement.

### Cas 3 : Vous alignez avec un LLM

Vous avez une question complexe : "Quelles sont les conditions d'une exception pour les États en développement ?"

**Avant le pipeline** :
- Utiliser ChatGPT
- Réponse peut être hallucination ou fausse
- Pas de source vérifiable

**Avec le pipeline (RAG)** :
- Rechercher dans l'ontologie les exceptions concernant États en développement
- Injecter le contexte exact dans le LLM
- LLM répond en se basant sur des faits vérifiés
- Vous avez les sources (Résolution X, Article Y)

---

## 🚀 Prochaines étapes (2 min)

Ouvrir cette architecture à 6 nouvelles interdictions :

**I003** : Filets maillants dérivants (FAO)  
**I004** : Pêche IUU (Illegal, Unreported, Unregulated) — FAO Agreement  
**I005** : Pêche électrique — Résolutions UE + régionales  
**I006** : Explosifs de pêche — Conventions internationales  
**I007** : Cyanure de pêche — Code conduite FAO  
**I008** : Chasse aux mammifères marins — MARPOL + conventions régionales  

Le pipeline est prêt. Les **templates sont là**. On doit juste remplir avec vos données.

Pour chacune, il faudra :
1. Extraire les zones d'application
2. Identifier les acteurs concernés
3. Lister les exceptions
4. Trouver les sources juridiques
5. Identifier les espèces/activités
6. Estimer la confidence (0.0-1.0)

Estimation : 1-2 jours par interdiction pour extraction manuelle + vérification.

---

## ⚖️ Avantages du système (2 min)

Récapitulons les bénéfices :

✅ **Structuration sémantique** — Passer de texte chaos à graphe organisé  
✅ **Requêtabilité** — Poser des questions machines (SPARQL)  
✅ **Multi-format** — TTL pour devs, OWL pour Protégé, JSON-LD pour web  
✅ **RAG-ready** — Intégré avec LLMs pour augmentation de réponses  
✅ **Validation** — 12 tests de compétence inclus  
✅ **Extensibilité** — 8 interdictions prêtes, facile d'en ajouter  
✅ **Traçabilité** — Chaque triplet a une source vérifiable  
✅ **Gouvernance** — Chaque fait peut être revu/approuvé  

---

## ❓ Questions courantes (2 min)

### "Ce système peut-il gérer des mises à jour ?"

**Oui** — Vous modifiez interdictions.yaml, vous relancez `python main.py`. Nouvelle ontologie générée. Version contrôlée via Git.

### "Et la performance ? Avec 1000+ triplets ?"

**Rapide** — SPARQL sur 1000-10000 triplets = exécution instantanée. Neo4j peut gérer millions de triplets.

### "Et la sécurité des données ?"

**À la main du client** — Vous hébergez tout en local. Données pas envoyées à un serveur tiers (sauf si vous déployez Fuseki/Neo4j publiquement).

### "Ça marche avec d'autres domaines juridiques ?"

**Absolument** — Le pipeline est générique. On l'a adapté au maritime, mais ça marche pour droit pénal, droit du travail, etc. Juste changer le schéma et les données.

---

## 🎬 Démonstration live (5 min)

[Ouvrir Protégé avec maritime_ontology.owl]

Montrer :
1. Hiérarchie des classes (Zone → ZoneHauteMer, etc.)
2. Cliquer sur InterdictionChalutagedefond
3. Voir les propriétés (appliesInZone, aException, etc.)
4. Voir les individus liés

[Ouvrir Neo4j Browser]

Exécuter :
```cypher
MATCH (n:Interdiction)-[r]->(m) LIMIT 50
RETURN n, r, m
```

Voir le graphe visuel avec nœuds interconnectés.

[Ouvrir Fuseki SPARQL Endpoint]

Exécuter une requête :
```sparql
SELECT ?zone WHERE {
  mar:InterdictionChalutagedefond mar:appliesInZone ?zone .
}
```

Voir les résultats en direct.

---

## 🏁 Conclusion (2 min)

En résumé :

**Notre pipeline maritime devient le fondement d'un système intelligent** pour naviguer le droit international de la mer. 

Au lieu d'avoir des PDFs éparpillés ou des conversations confuses avec des LLMs, vous avez :
1. **Une source de vérité unique** — l'ontologie RDF
2. **Des requêtes précises** — SPARQL au service des données
3. **Une augmentation sémantique** — pour des LLMs plus fiables
4. **Une extensibilité** — de 2 à 8 interdictions et plus

C'est l'avenir du droit digital : **structurer la connaissance juridique comme une machine peut la comprendre**.

---

**Merci de votre attention !**

Des questions ?

---

## 📎 Appendice : Jargon démystifié

**RDF** : Resource Description Framework — langage pour encoder le Web sémantique (triplets sujet-prédicat-objet)

**OWL** : Web Ontology Language — extension de RDF avec plus de sémantique (classes, propriétés, restrictions)

**SKOS** : Simple Knowledge Organization System — langage pour vocabs, thésaurus, glossaires

**SPARQL** : Query language pour RDF (comme SQL pour databases)

**Neo4j** : Base de données graphe — stocke et requête efficacement les relations

**Turtle (.ttl)** : Format RDF lisible par humains

**Protégé** : Éditeur graphique pour ontologies OWL

**Fuseki** : Serveur SPARQL (endpoint pour requêtes distantes)

**RAG** : Retrieval-Augmented Generation — augmenter LLMs avec une base de connaissances externe
