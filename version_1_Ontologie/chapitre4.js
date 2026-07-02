const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, HeadingLevel, LevelFormat, BorderStyle, WidthType,
  ShadingType, VerticalAlign, PageNumber, PageBreak
} = require('docx');
const fs = require('fs');

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 200 },
    children: [new TextRun({ text, bold: true, size: 32, font: "Arial" })]
  });
}

function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 280, after: 160 },
    children: [new TextRun({ text, bold: true, size: 28, font: "Arial" })]
  });
}

function h3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    spacing: { before: 200, after: 120 },
    children: [new TextRun({ text, bold: true, size: 24, font: "Arial" })]
  });
}

function body(text, options = {}) {
  return new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { before: 100, after: 100, line: 276 },
    children: [new TextRun({ text, font: "Arial", size: 22, ...options })]
  });
}

function bodyRuns(runs) {
  return new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { before: 100, after: 100, line: 276 },
    children: runs.map(r =>
      typeof r === 'string'
        ? new TextRun({ text: r, font: "Arial", size: 22 })
        : new TextRun({ font: "Arial", size: 22, ...r })
    )
  });
}

function bullet(text, bold_prefix = null) {
  const children = [];
  if (bold_prefix) {
    children.push(new TextRun({ text: bold_prefix, font: "Arial", size: 22, bold: true }));
    children.push(new TextRun({ text, font: "Arial", size: 22 }));
  } else {
    children.push(new TextRun({ text, font: "Arial", size: 22 }));
  }
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { before: 60, after: 60, line: 276 },
    children
  });
}

function code(text) {
  return new Paragraph({
    spacing: { before: 80, after: 80 },
    indent: { left: 720 },
    children: [new TextRun({
      text,
      font: "Courier New",
      size: 18,
      color: "1F497D"
    })]
  });
}

function caption(text) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 80, after: 160 },
    children: [new TextRun({ text, font: "Arial", size: 20, italics: true, color: "555555" })]
  });
}

function makeTable(headers, rows, colWidths) {
  const totalWidth = colWidths.reduce((a, b) => a + b, 0);
  const headerRow = new TableRow({
    children: headers.map((h, i) => new TableCell({
      borders,
      width: { size: colWidths[i], type: WidthType.DXA },
      shading: { fill: "2E5090", type: ShadingType.CLEAR },
      margins: { top: 80, bottom: 80, left: 120, right: 120 },
      verticalAlign: VerticalAlign.CENTER,
      children: [new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: h, font: "Arial", size: 20, bold: true, color: "FFFFFF" })]
      })]
    }))
  });
  const dataRows = rows.map((row, ri) => new TableRow({
    children: row.map((cell, ci) => new TableCell({
      borders,
      width: { size: colWidths[ci], type: WidthType.DXA },
      shading: { fill: ri % 2 === 0 ? "F2F6FC" : "FFFFFF", type: ShadingType.CLEAR },
      margins: { top: 80, bottom: 80, left: 120, right: 120 },
      children: [new Paragraph({
        alignment: ci === 0 ? AlignmentType.LEFT : AlignmentType.CENTER,
        children: [new TextRun({ text: cell, font: "Arial", size: 20 })]
      })]
    }))
  }));
  return new Table({
    width: { size: totalWidth, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: [headerRow, ...dataRows]
  });
}

const doc = new Document({
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "\u2022",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } }
        }]
      },
      {
        reference: "numbered",
        levels: [{
          level: 0, format: LevelFormat.DECIMAL, text: "%1.",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } }
        }]
      }
    ]
  },
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial", color: "1F3864" },
        paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 }
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial", color: "2E5090" },
        paragraph: { spacing: { before: 280, after: 160 }, outlineLevel: 1 }
      },
      {
        id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: "Arial", color: "375623" },
        paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 }
      }
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1800 }
      }
    },
    children: [

      // ══════════════════════════════════════════════════════════
      // TITRE DU CHAPITRE
      // ══════════════════════════════════════════════════════════
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        spacing: { before: 0, after: 280 },
        children: [new TextRun({ text: "Chapitre 4 : Construction du Graphe de Connaissances", bold: true, size: 36, font: "Arial", color: "1F3864" })]
      }),

      body("Ce chapitre décrit le processus complet de construction du graphe de connaissances maritime, depuis l'extraction automatique des informations juridiques contenues dans les textes bruts jusqu'à leur représentation exploitable dans une base Neo4j. Il couvre successivement l'extraction des entités et des relations, la transformation de l'ontologie OWL vers le modèle de graphe de propriétés, l'architecture de la base construite, son analyse structurelle, et enfin les limites inhérentes à la modélisation retenue."),

      new Paragraph({ spacing: { before: 200 } }),

      // ══════════════════════════════════════════════════════════
      // 4.1
      // ══════════════════════════════════════════════════════════
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        spacing: { before: 320, after: 200 },
        children: [new TextRun({ text: "4.1  Extraction des connaissances à partir du texte", bold: true, size: 32, font: "Arial", color: "1F3864" })]
      }),

      body("La transformation de textes juridiques bruts en triplets RDF structurés constitue l'étape fondatrice du graphe de connaissances. Cette opération repose sur deux tâches complémentaires : la reconnaissance d'entités nommées (NER) et l'extraction de relations. La particularité du corpus maritime, composé de conventions internationales rédigées en langage juridique formel, impose une stratégie d'extraction multi-modèles afin de garantir exhaustivité et précision."),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 280, after: 160 },
        children: [new TextRun({ text: "4.1.1  Stratégie multi-modèles pour l'extraction des triplets", bold: true, size: 28, font: "Arial", color: "2E5090" })]
      }),

      body("La première phase du pipeline d'extraction concerne la production de triplets RDF de la forme {Sujet, Prédicat, Objet} à partir des documents juridiques. Plutôt que de s'appuyer sur un unique modèle de langage, une approche comparative a été adoptée, mobilisant simultanément deux systèmes aux architectures distinctes : Claude Sonnet 4.6 et LlamaParser."),

      body("Ce choix délibéré repose sur la complémentarité des deux modèles. Une analyse comparative approfondie, conduite sur l'ensemble du corpus, a mis en évidence des différences significatives tant en volume qu'en nature des informations extraites. Sur l'interdiction relative au chalutage de fond (I001), Claude Sonnet 4.6 a extrait 31 entités et 39 triplets, tandis que LlamaParser en a produit respectivement 70 et 200, avec seulement 29 triplets en commun. L'écart est encore plus prononcé sur l'interdiction relative aux baleines (I002) : Claude Sonnet 4.6 a fourni 38 entités et 40 triplets, contre 331 entités et 329 triplets pour LlamaParser, avec seulement 6 triplets communs."),

      new Paragraph({ spacing: { before: 120 } }),

      makeTable(
        ["Interdiction", "Modèle", "Entités extraites", "Triplets extraits", "Triplets communs"],
        [
          ["I001 — Chalutage de fond", "Claude Sonnet 4.6", "31", "39", "29"],
          ["I001 — Chalutage de fond", "LlamaParser", "70", "200", "29"],
          ["I002 — Chasse baleine", "Claude Sonnet 4.6", "38", "40", "6"],
          ["I002 — Chasse baleine", "LlamaParser", "331", "329", "6"],
        ],
        [2200, 2000, 1500, 1500, 1500]
      ),
      caption("Tableau 4.1 — Comparaison des résultats d'extraction entre Claude Sonnet 4.6 et LlamaParser"),

      new Paragraph({ spacing: { before: 120 } }),

      body("Ces chiffres illustrent une réalité fondamentale : les deux modèles ne capturent pas les mêmes informations. Claude Sonnet 4.6 produit des extractions plus concises et précises, favorisant la qualité sur la quantité, tandis que LlamaParser génère un volume plus important de triplets en capturant davantage de variantes et de détails techniques. Les résultats des deux modèles ont donc été fusionnés en conservant l'intégralité des informations extraites, sans doublon, dans six fichiers JSON distincts par interdiction."),

      body("Avant leur intégration dans le pipeline ontologique, ces données fusionnées ont été soumises à une validation par des experts du domaine juridique maritime. Cette étape a permis de vérifier la cohérence sémantique des entités et triplets produits, de corriger les erreurs d'extraction résiduelles et de résoudre les ambiguïtés terminologiques. Elle constitue le dernier verrou de qualité garantissant que la matière première du graphe repose sur des informations à la fois exhaustives et rigoureusement vérifiées."),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 280, after: 160 },
        children: [new TextRun({ text: "4.1.2  Extraction des définitions juridiques", bold: true, size: 28, font: "Arial", color: "2E5090" })]
      }),

      body("Parallèlement à l'extraction des triplets, un second volet a été consacré à l'extraction des définitions juridiques contenues dans les textes. Cette tâche présente une difficulté spécifique : chaque convention internationale recourt à une terminologie propre, et la précision des définitions est déterminante pour la qualité du raisonnement que le graphe devra supporter."),

      body("Pour ce faire, un pool de quatre modèles de langage a été mobilisé en parallèle : Mistral-8B, LlamaParser, Gemma-4-E4B-it et Qwen. L'analyse comparative des résultats a permis d'identifier, pour chaque thématique juridique, le modèle le plus performant. Mistral-8B s'est distingué sur les documents relatifs aux engins de pêche, en raison de sa capacité à traiter un volume élevé de termes techniques simples. LlamaParser s'est imposé comme le modèle de référence pour les documents à forte densité scientifique, notamment pour les conventions ICRW et MARPOL, où il extrait les paramètres techniques (noms scientifiques, formules, seuils réglementaires) avec une fidélité remarquable. Gemma-4-E4B-it a quant à lui produit les résultats les plus propres sur les définitions juridiques françaises, notamment pour les documents relatifs à la Gestion Intégrée des Zones Côtières et à la Convention sur les Espèces Migratrices."),

      body("Sur la base de cette évaluation, une stratégie de sélection par thématique a été adoptée : plutôt que de retenir un unique modèle pour l'ensemble du corpus, le meilleur résultat a été conservé domaine par domaine, garantissant ainsi une extraction à la fois exhaustive et précise."),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 280, after: 160 },
        children: [new TextRun({ text: "4.1.3  Pipeline d'injection qualifiée des triplets", bold: true, size: 28, font: "Arial", color: "2E5090" })]
      }),

      body("Une fois les triplets produits par les LLM, leur injection dans le graphe RDF est assurée par le module triple_injector.py selon un pipeline en quatre phases successives."),

      body("La Phase 1 constitue l'injection proprement dite : chaque triplet JSON de la forme {sujet, prédicat, objet} est transformé en un arc RDF réel dans le graphe. Les prédicats bruts extraits par les modèles sont normalisés via une table de correspondance (PREDICATE_MAP). Par exemple, le prédicat générique mar:admetException produit par un LLM est automatiquement réécrit en mar:aException, qui correspond à la propriété d'objet définie dans la T-Box de l'ontologie."),

      body("Un filtre de confiance est appliqué en amont de cette injection : seuls les triplets dont le score de confiance attribué par le modèle est supérieur ou égal à 0,8 (CONFIDENCE_THRESHOLD) sont intégrés au graphe. Cette règle permet d'éliminer les extractions incertaines et de réduire le bruit sémantique."),

      body("Une normalisation géographique est également appliquée afin d'éviter la prolifération des entités spatiales. Un dictionnaire de normalisation (ZONE_MAPPING) résout tous les synonymes courants vers un identifiant canonique unique. Ainsi, les expressions « high seas », « au-delà de la juridiction nationale » ou « zone internationale » sont toutes résolues vers l'identifiant HM (Haute Mer)."),

      body("La Phase 2 assure le typage OWL des entités extraites par NER : chaque entité est rattachée à la classe OWL appropriée via la table CATEGORY_TO_OWL_CLASS. Une entité détectée comme appartenant à la catégorie « Actor » est automatiquement instanciée comme individu de la classe mar:Acteur."),

      body("La Phase 3 matérialise les inférences que Neo4j ne peut pas calculer nativement, faute de raisonneur en logique de description. Trois règles sont systématiquement appliquées : (1) toute Zone liée à une Interdiction reçoit le label supplémentaire :ZoneInterdite ; (2) toute Activité liée à une Interdiction reçoit le label :ActiviteIllicite ; (3) la chaîne de propriétés pratiqueActivite ∘ estActiviteDe est résolue pour produire la relation directe estSoumisA entre un Acteur et une Interdiction."),

      body("La Phase 4 assure enfin la liaison des définitions juridiques retenues au graphe, en créant des arcs mar:hasConcept entre chaque nœud Interdiction et les concepts lexicaux SKOS qui lui sont associés."),

      body("Un filtre de cohérence juridique transversal complète ce dispositif en bloquant les associations sémantiquement absurdes : par exemple, l'association de l'interdiction I003 (Construction Littorale) à la zone HM (Haute Mer) est systématiquement rejetée, car aucune activité de construction côtière ne peut s'exercer en haute mer."),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 280, after: 160 },
        children: [new TextRun({ text: "4.1.4  Génération de la couche lexicale et des synonymes", bold: true, size: 28, font: "Arial", color: "2E5090" })]
      }),

      body("Un troisième volet du pipeline d'extraction concerne la génération des synonymes. Claude Sonnet 4.6 a été sollicité dans une passe dédiée pour produire, pour chaque entité extraite, l'ensemble des termes alternatifs susceptibles d'être employés dans des textes nationaux pour désigner la même réalité juridique. Ces synonymes sont encodés en RDF via la propriété SKOS skos:altLabel et jouent un rôle central dans la résolution des requêtes du système RAG, en permettant de retrouver une entité même lorsque la formulation employée par l'utilisateur diffère du vocabulaire contrôlé de l'ontologie."),

      new Paragraph({ spacing: { before: 200 } }),

      // ══════════════════════════════════════════════════════════
      // 4.2
      // ══════════════════════════════════════════════════════════
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        spacing: { before: 320, after: 200 },
        children: [new TextRun({ text: "4.2  Passage de l'ontologie OWL vers le graphe de propriétés", bold: true, size: 32, font: "Arial", color: "1F3864" })]
      }),

      body("L'ontologie OWL 2 DL construite dans le chapitre précédent repose sur un formalisme de logique de description (DL), adapté au raisonnement automatique mais peu exploitable directement pour les besoins d'un système de recherche à grande échelle. La transition vers un graphe de propriétés Neo4j est assurée par le module neo4j_export.py, qui traduit les primitives OWL en structures natives du modèle Property Graph."),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 280, after: 160 },
        children: [new TextRun({ text: "4.2.1  Mapping des primitives OWL vers Neo4j", bold: true, size: 28, font: "Arial", color: "2E5090" })]
      }),

      body("La conversion repose sur trois règles de mapping systématiques."),

      body("Premièrement, chaque individu OWL (owl:NamedIndividual) devient un nœud Neo4j. Les labels du nœud sont déterminés par résolution des classes OWL auxquelles appartient l'individu via la table CLASS_TO_NEO4J_LABEL. Un individu de la classe ZoneEconomiqueExclusive reçoit ainsi les deux labels :Zone et :ZoneEEZ, ce qui permet à la fois des requêtes génériques (sur toutes les zones) et des requêtes spécifiques (sur les ZEE uniquement). Cette multi-labellisation préserve la sémantique héritée de la hiérarchie de classes OWL."),

      body("Deuxièmement, chaque propriété d'objet OWL est transformée en type de relation Neo4j, en respectant la convention de nommage SCREAMING_SNAKE_CASE. La propriété appliesInZone devient ainsi la relation [:APPLIES_IN_ZONE], concerneActeur devient [:CONCERNE_ACTEUR], et protegeEspece devient [:PROTEGE_ESPECE]. L'intégralité du mapping est définie dans la table PREDICATE_TO_RELATION."),

      body("Troisièmement, les propriétés de données OWL (owl:DatatypeProperty) sont injectées comme attributs des nœuds. La table DATA_PROPS liste les propriétés exportées : confidence, legalLayer, nomScientifique, sourceYear, definition, synonym, parmi d'autres."),

      new Paragraph({ spacing: { before: 120 } }),

      makeTable(
        ["Primitive OWL", "Équivalent Neo4j", "Exemple"],
        [
          ["owl:NamedIndividual (classe C)", "Nœud avec labels issus de C", "ZoneEEZ → :Zone:ZoneEEZ"],
          ["owl:ObjectProperty", "Relation typée en SNAKE_CASE", "appliesInZone → [:APPLIES_IN_ZONE]"],
          ["owl:DatatypeProperty", "Attribut de nœud", "sourceYear → propriété {sourceYear: 1982}"],
          ["skos:altLabel", "Nœud :Synonyme + relation [:SYNONYME_DE]", "\"high seas\" → :Synonyme lié à HM"],
          ["rdfs:label (fr/en)", "Attribut {label, label_en}", "label: \"Haute Mer\", label_en: \"High Seas\""],
        ],
        [2200, 2600, 2800]
      ),
      caption("Tableau 4.2 — Table de correspondance des primitives OWL vers le modèle de graphe de propriétés Neo4j"),

      new Paragraph({ spacing: { before: 120 } }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 280, after: 160 },
        children: [new TextRun({ text: "4.2.2  Gestion de la sémantique héritée", bold: true, size: 28, font: "Arial", color: "2E5090" })]
      }),

      body("Neo4j ne supporte pas nativement l'héritage de classes ni le raisonnement OWL. La sémantique héritée est donc préservée par deux mécanismes complémentaires. D'une part, la multi-labellisation des nœuds encode statiquement la hiérarchie : un nœud appartenant à ChasseCommerciale reçoit également les labels Activite et ChasseBaleine, reflétant la chaîne de subsomption. D'autre part, la matérialisation des inférences (Phase 3 du pipeline) pré-calcule les relations logiquement déductibles de l'ontologie, en particulier les labels :ZoneInterdite et :ActiviteIllicite ainsi que la relation [:EST_SOUMIS_A] issue de la chaîne de propriétés."),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 280, after: 160 },
        children: [new TextRun({ text: "4.2.3  Gestion de la couche lexicale (synonymes SKOS)", bold: true, size: 28, font: "Arial", color: "2E5090" })]
      }),

      body("La couche lexicale bénéficie d'un traitement spécifique. Chaque propriété skos:altLabel associée à une entité est extraite pour créer un nœud de type :Synonyme, contenant le texte alternatif comme propriété label. Ce nœud est relié à l'entité principale par une relation [:SYNONYME_DE]. Ce mécanisme permet au système RAG d'associer une requête formulée avec un terme non standard à l'entité canonique correspondante, garantissant ainsi la robustesse de la recherche face à la variété terminologique propre aux textes juridiques nationaux."),

      new Paragraph({ spacing: { before: 200 } }),

      // ══════════════════════════════════════════════════════════
      // 4.3
      // ══════════════════════════════════════════════════════════
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        spacing: { before: 320, after: 200 },
        children: [new TextRun({ text: "4.3  Construction et peuplement du graphe (Neo4j)", bold: true, size: 32, font: "Arial", color: "1F3864" })]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 280, after: 160 },
        children: [new TextRun({ text: "4.3.1  Architecture retenue et noyau expert", bold: true, size: 28, font: "Arial", color: "2E5090" })]
      }),

      body("Le graphe est construit de manière incrémentale, en partant d'un noyau expert composé des six interdictions maritimes internationales les plus emblématiques. Ce noyau, peuplé par le module populator.py, constitue le point d'ancrage sémantique autour duquel l'ensemble des entités du domaine sont organisées."),

      body("Chacune des six interdictions pivots fédère un sous-graphe cohérent, reliant sources juridiques, zones d'application, acteurs concernés, activités réglementées et espèces protégées :"),

      bullet(" I001 — Chalutage de fond : lié aux résolutions AGNU (61/105, 64/72, 66/68, 71/123) et aux zones d'Écosystèmes Marins Vulnérables (ZEV) et de Haute Mer.", null),
      bullet(" I002 — Chasse à la baleine : lié à la convention ICRW (1946), à la Commission Baleinière Internationale (IWC), et à quinze espèces de cétacés mysticètes et odontocètes.", null),
      bullet(" I003 — Construction littorale : lié à la Loi Littoral française (1986) et au Protocole GIZC de la Méditerranée (2008).", null),
      bullet(" I004 — Extraction de sable marin : lié à la Convention sur la Diversité Biologique (CDB, 1992) et aux zones côtières et ZEE.", null),
      bullet(" I005 — Oiseaux marins migrateurs : lié à la Convention CMS (Bonn, 1979) et à l'Accord ACAP (2004), couvrant albatros, pétrels et sternes.", null),
      bullet(" I006 — Rejets d'hydrocarbures : lié à MARPOL 73/78 et à ses six zones spéciales (Méditerranée, Baltique, Mer Noire, Mer Rouge, Golfe Persique, Antarctique).", null),

      new Paragraph({ spacing: { before: 100 } }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 280, after: 160 },
        children: [new TextRun({ text: "4.3.2  Schéma de la base (labels, relations, propriétés)", bold: true, size: 28, font: "Arial", color: "2E5090" })]
      }),

      body("La base Neo4j repose sur un schéma structuré autour de dix types de nœuds principaux et d'une quinzaine de types de relations."),

      new Paragraph({ spacing: { before: 100 } }),

      makeTable(
        ["Label Neo4j", "Description", "Propriétés clés"],
        [
          [":Interdiction", "Norme déontique prohibitive", "id, label, deonticType, legalLayer, confidence"],
          [":Zone", "Espace maritime réglementé", "id, label, distanceNM, codeZoneIMO"],
          [":Activite", "Activité maritime réglementée", "id, label, typeActivite"],
          [":Acteur", "Agent soumis aux normes", "id, label, type"],
          [":EspeceMarine", "Taxon marin protégé", "id, label, nomScientifique, statutProtection"],
          [":SourceJuridique", "Instrument de droit international", "id, label, sourceYear, sourceReference"],
          [":ExceptionJuridique", "Dérogation à une interdiction", "id, label, comment"],
          [":Controle", "Mécanisme de surveillance", "id, label, definition"],
          [":Sanction", "Conséquence de la violation", "id, label, definition"],
          [":ConceptLexical", "Terme du glossaire SKOS", "id, label, definition, nomScientifique"],
        ],
        [2000, 2600, 3000]
      ),
      caption("Tableau 4.3 — Labels de nœuds Neo4j et propriétés associées"),

      new Paragraph({ spacing: { before: 160 } }),

      makeTable(
        ["Type de relation", "Source → Cible", "Sémantique"],
        [
          ["[:APPLIES_IN_ZONE]", "Interdiction → Zone", "Portée géographique de la norme"],
          ["[:CONCERNE_ACTIVITE]", "Interdiction → Activite", "Activité réglementée"],
          ["[:CONCERNE_ACTEUR]", "Interdiction → Acteur", "Acteur destinataire de la norme"],
          ["[:PROTEGE_ESPECE]", "Interdiction → EspeceMarine", "Espèce visée par la protection"],
          ["[:FONDEE_SUR]", "Interdiction → SourceJuridique", "Base juridique de la norme"],
          ["[:A_EXCEPTION]", "Interdiction → ExceptionJuridique", "Dérogation applicable"],
          ["[:ENTRAINE_SANCTION]", "Interdiction → Sanction", "Conséquence de la violation"],
          ["[:EST_SOUMIS_A]", "Acteur → Interdiction", "Obligation (inférence matérialisée)"],
          ["[:HAS_CONCEPT]", "Interdiction → ConceptLexical", "Terme du glossaire associé"],
          ["[:SYNONYME_DE]", "Synonyme → Nœud", "Pont lexical pour la recherche"],
        ],
        [2400, 2400, 2800]
      ),
      caption("Tableau 4.4 — Types de relations Neo4j et leur sémantique"),

      new Paragraph({ spacing: { before: 160 } }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 280, after: 160 },
        children: [new TextRun({ text: "4.3.3  Contraintes, indexation et requêtes Cypher", bold: true, size: 28, font: "Arial", color: "2E5090" })]
      }),

      body("Afin de garantir l'intégrité du graphe, une contrainte d'unicité est créée sur la propriété id pour chaque label principal de nœud. Ces contraintes sont générées automatiquement lors de l'export :"),

      code("CREATE CONSTRAINT IF NOT EXISTS FOR (n:Interdiction) REQUIRE n.id IS UNIQUE;"),
      code("CREATE CONSTRAINT IF NOT EXISTS FOR (n:Zone) REQUIRE n.id IS UNIQUE;"),
      code("CREATE CONSTRAINT IF NOT EXISTS FOR (n:EspeceMarine) REQUIRE n.id IS UNIQUE;"),

      body("Un index fulltext nommé maritimeSearch est créé sur les propriétés textuelles des nœuds les plus interrogés, permettant une recherche rapide par mots-clés :"),

      code("CREATE FULLTEXT INDEX maritimeSearch IF NOT EXISTS"),
      code("FOR (n:Interdiction|Zone|Activite|Acteur|EspeceMarine|ConceptLexical)"),
      code("ON EACH [n.label, n.label_en, n.definition, n.nomScientifique];"),

      body("À titre d'exemple, la requête Cypher suivante permet de retrouver toutes les zones dans lesquelles s'applique l'interdiction du chalutage de fond, ainsi que leurs espèces protégées associées :"),

      code("MATCH (i:Interdiction {id: 'I001'})-[:APPLIES_IN_ZONE]->(z:Zone)"),
      code("OPTIONAL MATCH (i)-[:PROTEGE_ESPECE]->(e:EspeceMarine)"),
      code("RETURN i.label, collect(DISTINCT z.label) AS zones,"),
      code("       collect(DISTINCT e.nomScientifique) AS especes;"),

      body("La requête d'inférence suivante exploite la relation matérialisée [:EST_SOUMIS_A] pour identifier tous les acteurs directement assujettis à une interdiction donnée :"),

      code("MATCH (a:Acteur)-[:EST_SOUMIS_A]->(i:Interdiction)"),
      code("WHERE i.id = 'I002'"),
      code("RETURN a.label AS acteur, i.label AS interdiction;"),

      new Paragraph({ spacing: { before: 200 } }),

      // ══════════════════════════════════════════════════════════
      // 4.5
      // ══════════════════════════════════════════════════════════
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        spacing: { before: 320, after: 200 },
        children: [new TextRun({ text: "4.5  Analyse structurelle du graphe", bold: true, size: 32, font: "Arial", color: "1F3864" })]
      }),

      body("Une fois le graphe construit, son analyse structurelle permet de faire ressortir les propriétés topologiques les plus révélatrices de l'organisation du droit maritime international. Cette analyse s'appuie sur des métriques de centralité, une détection de communautés et une exploration des chemins reliant les différentes catégories d'entités."),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 280, after: 160 },
        children: [new TextRun({ text: "4.5.1  Centralité et nœuds structurellement dominants", bold: true, size: 28, font: "Arial", color: "2E5090" })]
      }),

      body("Les six nœuds d'interdiction (I001 à I006) constituent les hubs à plus haute centralité de degré du graphe. Chacun concentre un nombre élevé de relations sortantes vers les zones, activités, acteurs et sources juridiques. Cette position centrale reflète leur rôle de « pivot normatif » : toute l'organisation du droit maritime gravitite autour de ces normes prohibitives."),

      body("Les nœuds de sources juridiques (UNCLOS, MARPOL, ICRW, CDB, CMS) occupent quant à eux une position de centralité d'intermédiarité élevée. Ils constituent les ponts obligatoires entre les interdictions déontiques et les acteurs institutionnels qui en assurent la mise en œuvre (IMO, IWC, FAO). Cette position confère aux sources juridiques un rôle d'ancrage stable : toute modification d'une convention affecte directement l'ensemble des normes qui y sont fondées."),

      body("La requête suivante calcule le degré entrant de chaque nœud, permettant d'identifier les entités les plus référencées :"),

      code("MATCH (n)<-[r]-()"),
      code("WITH n, count(r) AS degre_entrant"),
      code("WHERE degre_entrant > 3"),
      code("RETURN n.label, labels(n) AS types, degre_entrant"),
      code("ORDER BY degre_entrant DESC LIMIT 20;"),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 280, after: 160 },
        children: [new TextRun({ text: "4.5.2  Communautés de concepts et cohérence thématique", bold: true, size: 28, font: "Arial", color: "2E5090" })]
      }),

      body("L'analyse des communautés révèle que le graphe se structure naturellement en six clusters thématiques correspondant aux six interdictions, chacun regroupant les entités qui lui sont spécifiquement liées. Ces clusters ne sont pas totalement isolés : des nœuds partagés, comme la zone de Haute Mer (HM) ou l'entité « États Souverains », créent des ponts inter-communautés traduisant la transversalité de certains principes du droit maritime international."),

      body("Un cluster particulièrement dense se forme autour de I002 (Chasse à la Baleine), qui fédère quinze espèces de cétacés, quatre types d'acteurs (navires-usines, bateaux chasseurs, membres IWC, communautés autochtones), deux permissions distinctes (chasse scientifique et chasse de subsistance), et quatre zones de protection. Cette densité reflète la complexité exceptionnelle du régime juridique institué par l'ICRW."),

      body("Les nœuds d'exception et de conséquence constituent un sous-graphe transversal intéressant : chaque exception est connectée à sa conséquence normative conditionnelle, formant des chaînes « si... alors... » qui encodent la logique conditionnelle du droit."),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 280, after: 160 },
        children: [new TextRun({ text: "4.5.3  Chemins de raisonnement et inférences exploitables", bold: true, size: 28, font: "Arial", color: "2E5090" })]
      }),

      body("L'un des intérêts majeurs du graphe de connaissances est sa capacité à supporter des chemins de raisonnement multi-sauts. Par exemple, à partir d'un navire pétrolier, il est possible de remonter en trois arêtes à l'ensemble des zones où ses rejets sont interdits, aux sanctions applicables, et aux mécanismes de contrôle correspondants."),

      body("La requête Cypher suivante illustre ce type de traversée :"),

      code("MATCH (a:Acteur {id: 'Acteur_NavirePetrolier'})"),
      code("-[:EST_SOUMIS_A]->(i:Interdiction)"),
      code("-[:APPLIES_IN_ZONE]->(z:Zone),"),
      code("(i)-[:ENTRAINE_SANCTION]->(s:Sanction)"),
      code("RETURN a.label, i.label, collect(z.label) AS zones, s.label AS sanction;"),

      body("Ce type de requête permet de répondre en temps réel à des questions complexes du domaine juridique maritime, sans nécessiter de reformulation manuelle : « Quelles sanctions s'appliquent à un navire pétrolier en Méditerranée ? » devient une traversée de graphe de trois niveaux."),

      body("L'analyse révèle également que la chaîne [:FONDEE_SUR] → [:MODIFIE_SOURCE] permet de tracer la généalogie juridique des normes : MARPOL 73/78 est liée à la résolution MEPC.117(52) qui l'amende, elle-même reliée aux interdictions I006. Cette modélisation diachronique des sources constitue une originalité du graphe par rapport aux bases de données juridiques traditionnelles."),

      new Paragraph({ spacing: { before: 200 } }),

      // ══════════════════════════════════════════════════════════
      // 4.6
      // ══════════════════════════════════════════════════════════
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        spacing: { before: 320, after: 200 },
        children: [new TextRun({ text: "4.6  Limites de la modélisation", bold: true, size: 32, font: "Arial", color: "1F3864" })]
      }),

      body("L'audit du graphe a permis d'identifier plusieurs limites structurelles et méthodologiques qui doivent être prises en compte pour interpréter correctement les résultats et orienter les développements futurs."),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 280, after: 160 },
        children: [new TextRun({ text: "4.6.1  Le problème des nœuds flottants", bold: true, size: 28, font: "Arial", color: "2E5090" })]
      }),

      body("Environ 400 nœuds ont été identifiés initialement comme des ConceptLexical isolés, non reliés au reste du graphe par des propriétés sémantiques. Ces nœuds flottants résultent de l'absence de typage OWL rigoureux lors des premières phases d'extraction : les entités extraites étaient stockées comme simples étiquettes textuelles plutôt qu'instanciées comme individus d'une classe OWL précise. Sans ces relations, ces nœuds ne participent pas au raisonnement du graphe et restent des îlots d'information inutilisables. La Phase 2 du pipeline (typage NER) a été spécifiquement conçue pour résoudre ce problème, mais son application reste conditionnée à la qualité des métadonnées de catégorisation produites par les LLM."),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 280, after: 160 },
        children: [new TextRun({ text: "4.6.2  Absence de raisonneur en logique de description", bold: true, size: 28, font: "Arial", color: "2E5090" })]
      }),

      body("Neo4j ne dispose pas de raisonneur natif en logique de description. L'utilisation de raisonneurs externes comme HermiT ou Pellet, qui permettraient de calculer automatiquement toutes les inférences déductibles de l'ontologie OWL, introduirait des coûts de calcul significatifs et des difficultés d'intégration dans l'architecture existante. La solution retenue de « matérialisation manuelle » des inférences (Phase 3) est performante mais présente un défaut majeur : elle nécessite d'anticiper à l'avance l'ensemble des règles d'inférence utiles. Toute règle non explicitement programmée ne sera pas calculée, ce qui peut conduire à des silences dans les réponses du système."),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 280, after: 160 },
        children: [new TextRun({ text: "4.6.3  Hallucinations de prédicats par les LLM", bold: true, size: 28, font: "Arial", color: "2E5090" })]
      }),

      body("Les modèles de langage ont tendance à utiliser des prédicats génériques là où l'ontologie exige des prédicats spécifiques. Par exemple, un LLM peut associer une espèce marine à une interdiction via le prédicat generique concerneActivite, alors que la T-Box de l'ontologie impose l'utilisation de protegeEspece pour ce type de relation. Ces hallucinations de prédicats entraînent des triplets syntaxiquement valides mais sémantiquement incorrects. Le pipeline inclut une table de correction (PREDICATE_MAP) et un mécanisme de forçage du prédicat correct en fonction de la catégorie de l'objet, mais ces règles de correction ne couvrent pas l'intégralité des cas possibles. Une couche de validation sémantique plus formelle, s'appuyant sur les contraintes de domaine et de portée de l'ontologie, constituerait une amélioration significative."),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 280, after: 160 },
        children: [new TextRun({ text: "4.6.4  Complexité de la modélisation temporelle", bold: true, size: 28, font: "Arial", color: "2E5090" })]
      }),

      body("La gestion des périodes temporelles (OWL-Time) représente la limite la plus difficile à surmonter dans la version actuelle. L'ontologie utilise des nœuds blancs RDF (BNodes) pour représenter les instants de début et de fin des intervalles temporels, conformément à la spécification OWL-Time. Lors de la conversion vers Neo4j, ces BNodes sont traduits en nœuds ordinaires, ce qui complique considérablement les comparaisons de dates en Cypher. Requêter « quelles normes étaient en vigueur entre 1990 et 2000 ? » nécessite de traverser deux niveaux de nœuds intermédiaires avant d'accéder aux valeurs de date. Une modélisation alternative, inlinant les dates directement comme propriétés des nœuds Periode, permettrait des requêtes temporelles nettement plus efficaces, au prix d'une perte de conformité avec le standard OWL-Time."),

      body("Ces quatre limites ne remettent pas en cause la validité globale de l'approche adoptée, mais elles délimitent précisément le périmètre dans lequel le graphe peut être exploité avec confiance, et orientent les axes d'amélioration prioritaires pour une version future du système."),

      new Paragraph({ spacing: { before: 200 } }),

    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync('/home/claude/chapitre4.docx', buffer);
  console.log('Document créé avec succès.');
});
