# 🏛️ L'Ontologie (T-Box / Le Modèle Théorique)

Ce document dresse l'inventaire des composants structurels de l'ontologie maritime codés dans `schema.py`. C'est le "moule" ou le plan d'architecture.

## 📊 Statistiques globales de l'Ontologie
*   **Total des classes OWL** : 119
*   **Propriétés Objet (Relations)** : ~30
*   **Format de représentation** : OWL 2 DL (Description Logic)
*   **Alignement supérieur** : LKIF-Core (Standard légal) et OWL-Time (Temps)

---

## 1. Hiérarchie des Classes Principales (Les concepts)

Les classes sont organisées de manière hiérarchique (Top-Down). Voici les branches principales :

### ⚖️ Les Normes (Aligné sur `lkif:Norm`)
*   `NormeJuridique`
    *   `Interdiction` (ex: chalutage)
    *   `Permission` (dérogations officielles)
    *   `Obligation`

### 🗺️ Les Zones (`Zone`)
*   `ZoneSouverainete` (ex: Mer Territoriale)
*   `ZoneEconomique` (ex: ZEE)
*   `ZoneInternationale` (ex: Haute Mer, Zone)
*   `AireMarineProtegee` (ex: Sanctuaire)
*   *Classe inférée* : `ZoneInterdite`

### 👤 Les Acteurs (`Acteur`)
*   `EtatSouverain` (Pavillon, Côtier, Port)
*   `Organisation` (ORGP, OMI, CBI)
*   `Navire` (Pétrolier, Chalutier, Navire-Usine)
*   `Individu` (Capitaine, Armateur)
*   *Classe inférée* : `ActeurEnInfraction`

### 🎣 Les Activités (`Activite`)
*   `ActiviteExploitation` (Pêche, Chasse baleinière, Extraction sable)
*   `ActivitePolluante` (Rejet d'hydrocarbures)
*   `ActiviteAmenagement` (Construction littorale)
*   *Classe inférée* : `ActiviteIllicite`

### 🛡️ Les Exceptions et Conséquences (`ExceptionJuridique`)
*   `ExceptionGenerale` (Portée large, ex: chasse scientifique)
*   `ExceptionSpecifique` (Cas précis, ex: quota Groenland)
*   `ConsequenceException` (Obligation qui découle de l'exception, ex: rapport)

### ⚖️ Sanctions et Contrôles
*   `Controle` (État du port, État du pavillon)
*   `SanctionPenale` (Amendes, prison)
*   `SanctionAdministrative` (Retrait de permis)

---

## 2. Les Propriétés Objet (Les flèches autorisées)

Ces propriétés définissent **comment** les concepts ont le droit de se connecter entre eux.

*   **Rattachement à l'Interdiction :**
    *   `appliesInZone` (Interdiction → Zone)
    *   `concerneActeur` (Interdiction → Acteur)
    *   `concerneActivite` (Interdiction → Activite)
    *   `protegeEspece` (Interdiction → EspeceMarine)
*   **Conséquences & Logique juridique :**
    *   `aException` (Interdiction → ExceptionJuridique)
    *   `entraineConsequence` (Exception → ConsequenceException)
    *   `entraineSanction` (Interdiction → Sanction)
    *   `soumisAControle` (Interdiction → Controle)
*   **Comportement des Acteurs :**
    *   `pratiqueActivite` (Acteur → Activite)
    *   `estSoumisA` (Acteur → Interdiction)

---

## 3. Les Axiomes et Règles de Raisonnement (La "Magie" OWL)

C'est ici que l'ontologie devient intelligente et permet de faire des déductions automatiques.

### A. Restrictions existentielles (Ce qui est obligatoire)
*   Toute `Interdiction` **DOIT** avoir au moins une `Zone` (*someValuesFrom*).
*   Toute `Exception` **DOIT** entraîner au moins une `ConsequenceException`.
*   Toute `Norme` **DOIT** être fondée sur une `SourceJuridique`.

### B. Classes équivalentes (Pour l'inférence automatique)
*   **Zone Interdite** : Une zone est automatiquement classée comme `ZoneInterdite` SI elle est visée par la propriété `appliesInZone` d'une `Interdiction`.
*   **Activité Illicite** : Une activité est classée comme `ActiviteIllicite` SI elle est visée par `concerneActivite`.
*   **Acteur en Infraction** : Tout `Acteur` qui pratique une activité classée comme `ActiviteIllicite` devient automatiquement un `ActeurEnInfraction`.

### C. Chaîne de propriétés (Property Chain)
*   `pratiqueActivite` + `estActiviteDe` ➡️ **`estSoumisA`**
    *   *Règle :* Si un capitaine (Acteur) pratique le rejet d'huile (Activité), et que le rejet d'huile est l'activité interdite par MARPOL (Interdiction), alors le système déduit tout seul que le capitaine `estSoumisA` MARPOL.

### D. Classes Disjointes (Contraintes d'intégrité)
*   `Zone` est disjointe de `Acteur` (Un bateau ne peut pas être une zone de mer).
*   `SanctionPenale` est disjointe de `SanctionAdministrative`.
*   `ExceptionGenerale` est disjointe de `ExceptionSpecifique`.
