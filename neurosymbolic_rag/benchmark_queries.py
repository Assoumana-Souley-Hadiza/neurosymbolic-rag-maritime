"""
benchmark_queries.py — 264 questions de benchmark (2 thèmes × 12 pays × 11 axes)
Thèmes : chasse à la baleine | rejet d'hydrocarbures
Source : résultats run6_final extraits des fichiers xlsx de benchmark.
"""

BENCHMARK_QUERIES = [

    # =========================================================================
    # THÈME 1 — CHASSE AUX BALEINES / MAMMIFÈRES MARINS
    # Pays : Bénin, Cameroun, Comores, Congo, Djibouti, Gabon, Guinée, Madagascar, Mauritanie, Sénégal, Togo, Tunisie
    # =========================================================================

    # --- Bénin ---

    {
        "id": "Q_BAL_001",
        "axe": 1,
        "axe_label": "Existence",
        "question": "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines au Bénin ?",
        "country": "Bénin",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 79 interdit la pêche, la détention et la commercialisation de toute espèce de "
            "mammifères aquatiques ou de tortues marines en République du Bénin."
        ),
        "relevant_keywords": ['interdit', 'baleine'],
    },

    {
        "id": "Q_BAL_002",
        "axe": 2,
        "axe_label": "Zonage",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines au Bénin qui "
            "précise que cette mesure n'est applicable qu'à certaines zones, aires ou régions ?"
        ),
        "country": "Bénin",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'existe pas un article portant sur l'interdiction des baleines (cétacés) qui précise que "
            "cette mesure n'est applicable qu'à certaines zones, aires ou régions au Bénin."
        ),
        "relevant_keywords": ['zone', 'mammifère'],
    },

    {
        "id": "Q_BAL_003",
        "axe": 3,
        "axe_label": "Temporalité",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines au Bénin qui "
            "précise que cette mesure n'est pas applicable en permanence (temporalité) ?"
        ),
        "country": "Bénin",
        "theme": "chasse_baleines",
        "ground_truth": "Non.",
        "relevant_keywords": ['période', 'mammifère'],
    },

    {
        "id": "Q_BAL_004",
        "axe": 4,
        "axe_label": "Types d\'activités concernées",
        "question": (
            "Est-ce qu'un texte juridique précise les types d'activités concernées par l'interdiction de la "
            "chasse des baleines au Bénin ?"
        ),
        "country": "Bénin",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 79 précise que la pêche, la détention et la commercialisation de toute espèce de "
            "mammifères aquatiques ou de tortues marines sont interdites en République du Bénin."
        ),
        "relevant_keywords": ['capture', 'mammifère'],
    },

    {
        "id": "Q_BAL_005",
        "axe": 5,
        "axe_label": "Exceptions hors santé/ordre/recherche",
        "question": (
            "Est-ce qu'un texte juridique mentionne des exceptions à l'interdiction de la chasse des baleines au "
            "Bénin ? Vérifie si ce texte inclut des exceptions relatives à d'autres domaines que de la santé, de "
            "l'ordre public et de la recherche."
        ),
        "country": "Bénin",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas d'exceptions mentionnées dans les articles juridiques fournis concernant "
            "l'interdiction de la chasse, de la pêche ou de la capture des baleines (cétacés) au Bénin."
        ),
        "relevant_keywords": [],
        "is_piege": True,
    },

    {
        "id": "Q_BAL_006",
        "axe": 6,
        "axe_label": "Exceptions / dérogations spécifiques",
        "question": (
            "Est-ce qu'un texte juridique mentionne des exceptions à l'interdiction de la chasse des baleines au "
            "Bénin ? Ne pas inclure les délais de mise en place de la loi. Les dérogations ou autorisations "
            "spécifiques constituent des exceptions."
        ),
        "country": "Bénin",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas d'exceptions mentionnées dans les articles juridiques fournis pour l'interdiction "
            "de la chasse, de la pêche ou de la capture des baleines (cétacés) au Bénin."
        ),
        "relevant_keywords": ['dérogation', 'mammifère'],
    },

    {
        "id": "Q_BAL_007",
        "axe": 7,
        "axe_label": "Sanction financière",
        "question": (
            "Est-ce qu'il existe un article qui précise que l'infraction à l'interdiction de la chasse des "
            "baleines au Bénin entraîne une sanction financière ?"
        ),
        "country": "Bénin",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 79 précise que la chasse, la pêche ou la capture de baleines (cétacés) est interdite "
            "au Bénin et entraîne une sanction financière."
        ),
        "relevant_keywords": ['amende', 'baleine'],
    },

    {
        "id": "Q_BAL_008",
        "axe": 8,
        "axe_label": "Sanction pénale",
        "question": (
            "Est-ce que l'infraction à l'interdiction de la chasse des baleines au Bénin entraîne une peine de "
            "prison ?"
        ),
        "country": "Bénin",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 79 de la loi-cadre n°2014-19 du 7 août 2014 relative à la pêche et à l'aquaculture en "
            "République du Bénin prévoit une peine d'emprisonnement pour toute personne qui contrevient à "
            "l'interdiction de la chasse, de la pêche ou de la capture des baleines (cétacés) au Bénin."
        ),
        "relevant_keywords": ['emprisonnement', 'baleine'],
    },

    {
        "id": "Q_BAL_009",
        "axe": 9,
        "axe_label": "Contrôle — acteurs institutionnels",
        "question": (
            "Est-ce que au Bénin, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction de la chasse des baleines ?"
        ),
        "country": "Bénin",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Article 41 : L'administration en charge de la pêche peut exiger qu'un ou plusieurs observateurs "
            "scientifiques ou chargés du contrôle soient embarqués sur tout navire de pêche autorisé à pratiquer "
            "la pêche industrielle dans les eaux maritimes sous juridiction béninoise.\nArticle 96 : Les agents "
            "compétents sont habilités à stopper, arraisonner, visiter et inspecter toute embarcation de pêche "
            "maritime ou continentale ou tout navire pratiquant la pêche dans les eaux sous juridiction "
            "béninoise. Ils peuvent également prélever des échantillons de produits de la pêche et saisir à titre "
            "conservatoire tout véhicule, navire, engin, filet, instrument ou produit de la pêche."
        ),
        "relevant_keywords": ['administration', 'baleine'],
    },

    {
        "id": "Q_BAL_010",
        "axe": 10,
        "axe_label": "Contrôle — temporalité",
        "question": (
            "Est-ce que au Bénin, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction de la chasse des baleines ? Si ces procédures existent, "
            "vérifiez si elles précisent des périodes (temporalité) spécifiques pour le contrôle du respect de "
            "l'interdiction de la chasse des baleines."
        ),
        "country": "Bénin",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 41 prévoit que l'administration en charge de la pêche peut exiger qu'un ou plusieurs "
            "observateurs scientifiques soient embarqués sur tout navire de pêche autorisé à pratiquer la pêche "
            "industrielle dans les eaux maritimes sous juridiction béninoise. Cette disposition permet de "
            "superviser et d'évaluer le respect de l'interdiction de la pêche des baleines (cétacés)."
        ),
        "relevant_keywords": ['période', 'baleine'],
    },

    {
        "id": "Q_BAL_011",
        "axe": 11,
        "axe_label": "Contrôle — zones",
        "question": (
            "Est-ce que au Bénin, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction de la chasse des baleines ? Si ces procédures existent, "
            "vérifiez si elles précisent des lieux ou zones spécifiques pour le contrôle du respect de "
            "l'interdiction de la chasse des baleines."
        ),
        "country": "Bénin",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 41 prévoit que l'administration en charge de la pêche peut exiger qu'un ou plusieurs "
            "observateurs scientifiques soient embarqués sur tout navire de pêche autorisé à pratiquer la pêche "
            "industrielle dans les eaux maritimes sous juridiction béninoise. Cette disposition permet un "
            "contrôle direct et spécifique pour garantir le respect de l'interdiction des baleines (cétacés)."
        ),
        "relevant_keywords": ['zone', 'baleine'],
    },

    # --- Cameroun ---

    {
        "id": "Q_BAL_012",
        "axe": 1,
        "axe_label": "Existence",
        "question": "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines au Cameroun ?",
        "country": "Cameroun",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 26(1) interdit la capture des espèces aquatiques intégralement protégées, y compris "
            "les baleines."
        ),
        "relevant_keywords": ['interdit', 'baleine'],
    },

    {
        "id": "Q_BAL_013",
        "axe": 2,
        "axe_label": "Zonage",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines au Cameroun qui "
            "précise que cette mesure n'est applicable qu'à certaines zones, aires ou régions ?"
        ),
        "country": "Cameroun",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Il n'y a pas d'article spécifique concernant l'interdiction de la chasse, pêche ou capture de "
            "baleines (cétacés) dans certaines zones ou régions du Cameroun dans les documents fournis."
        ),
        "relevant_keywords": ['zone', 'mammifère'],
    },

    {
        "id": "Q_BAL_014",
        "axe": 3,
        "axe_label": "Temporalité",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines au Cameroun qui "
            "précise que cette mesure n'est pas applicable en permanence (temporalité) ?"
        ),
        "country": "Cameroun",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas d'article portant sur l'interdiction des baleines avec une exception temporelle au "
            "Cameroun dans les documents fournis."
        ),
        "relevant_keywords": ['période', 'mammifère'],
    },

    {
        "id": "Q_BAL_015",
        "axe": 4,
        "axe_label": "Types d\'activités concernées",
        "question": (
            "Est-ce qu'un texte juridique précise les types d'activités concernées par l'interdiction de la "
            "chasse des baleines au Cameroun ?"
        ),
        "country": "Cameroun",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'Article 26(1) précise que la capture des espèces aquatiques intégralement protégées est "
            "interdite."
        ),
        "relevant_keywords": ['capture', 'mammifère'],
    },

    {
        "id": "Q_BAL_016",
        "axe": 5,
        "axe_label": "Exceptions hors santé/ordre/recherche",
        "question": (
            "Est-ce qu'un texte juridique mentionne des exceptions à l'interdiction de la chasse des baleines au "
            "Cameroun ? Vérifie si ce texte inclut des exceptions relatives à d'autres domaines que de la santé, "
            "de l'ordre public et de la recherche."
        ),
        "country": "Cameroun",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas d'exceptions mentionnées dans les articles fournis concernant l'interdiction de la "
            "chasse, de la pêche ou de la capture des baleines (cétacés) au Cameroun."
        ),
        "relevant_keywords": [],
        "is_piege": True,
    },

    {
        "id": "Q_BAL_017",
        "axe": 6,
        "axe_label": "Exceptions / dérogations spécifiques",
        "question": (
            "Est-ce qu'un texte juridique mentionne des exceptions à l'interdiction de la chasse des baleines au "
            "Cameroun ? Ne pas inclure les délais de mise en place de la loi. Les dérogations ou autorisations "
            "spécifiques constituent des exceptions."
        ),
        "country": "Cameroun",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas d'exceptions mentionnées dans les articles fournis pour l'interdiction de la "
            "chasse, de la pêche ou de la capture des baleines (cétacés) au Cameroun."
        ),
        "relevant_keywords": ['dérogation', 'mammifère'],
    },

    {
        "id": "Q_BAL_018",
        "axe": 7,
        "axe_label": "Sanction financière",
        "question": (
            "Est-ce qu'il existe un article qui précise que l'infraction à l'interdiction de la chasse des "
            "baleines au Cameroun entraîne une sanction financière ?"
        ),
        "country": "Cameroun",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'infraction à l'interdiction de la chasse, pêche ou capture des baleines (cétacés) au Cameroun "
            "entraîne une peine de prison selon l'article 81 de la loi n°2024/019 du 23 décembre 2024 régissant "
            "la pêche et l'aquaculture en République."
        ),
        "relevant_keywords": ['amende', 'baleine'],
    },

    {
        "id": "Q_BAL_019",
        "axe": 8,
        "axe_label": "Sanction pénale",
        "question": (
            "Est-ce que l'infraction à l'interdiction de la chasse des baleines au Cameroun entraîne une peine de "
            "prison ?"
        ),
        "country": "Cameroun",
        "theme": "chasse_baleines",
        "ground_truth": "Oui",
        "relevant_keywords": ['emprisonnement', 'baleine'],
    },

    {
        "id": "Q_BAL_020",
        "axe": 9,
        "axe_label": "Contrôle — acteurs institutionnels",
        "question": (
            "Est-ce que au Cameroun, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction de la chasse des baleines ?"
        ),
        "country": "Cameroun",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, au Cameroun, il existe une administration compétente pour superviser et évaluer l'application "
            "de l'interdiction de capture des espèces aquatiques intégralement protégées, y compris les baleines "
            "(cétacés). Cette interdiction est régie par la loi n° 2024/019 du 23 décembre 2024 régissant la "
            "pêche et l'aquaculture en République. Les agents de contrôle et de surveillance du Ministère en "
            "charge des pêches, en collaboration avec l'administration en charge de la faune et les communautés "
            "riveraines, assurent le suivi, le contrôle et la surveillance des activités de pêche dans les aires "
            "marines protégées (Article 35)."
        ),
        "relevant_keywords": ['administration', 'baleine'],
    },

    {
        "id": "Q_BAL_021",
        "axe": 10,
        "axe_label": "Contrôle — temporalité",
        "question": (
            "Est-ce que au Cameroun, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction de la chasse des baleines ? Si ces procédures existent, "
            "vérifiez si elles précisent des périodes (temporalité) spécifiques pour le contrôle du respect de "
            "l'interdiction de la chasse des baleines."
        ),
        "country": "Cameroun",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, il existe une administration compétente pour superviser et constater l'application de "
            "l'interdiction des espèces aquatiques intégralement protégées au Cameroun. Cette interdiction est "
            "spécifiquement décrite dans l'ARTICLE 26 de la loi n° 2024/019 du 23 décembre 2024 régissant la "
            "pêche et l'aquaculture en République. Les espèces aquatiques intégralement protégées capturées "
            "accidentellement doivent être immédiatement remises à l'eau, et si elles ne sont plus vivantes au "
            "moment de leur capture, une déclaration doit être faite aux administrations compétentes lors du "
            "débarquement. Les espèces aquatiques intégralement protégées débarquées sont systématiquement "
            "saisies par l'administration compétente."
        ),
        "relevant_keywords": ['période', 'baleine'],
    },

    {
        "id": "Q_BAL_022",
        "axe": 11,
        "axe_label": "Contrôle — zones",
        "question": (
            "Est-ce que au Cameroun, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction de la chasse des baleines ? Si ces procédures existent, "
            "vérifiez si elles précisent des lieux ou zones spécifiques pour le contrôle du respect de "
            "l'interdiction de la chasse des baleines."
        ),
        "country": "Cameroun",
        "theme": "chasse_baleines",
        "ground_truth": "",
        "relevant_keywords": ['zone', 'baleine'],
    },

    # --- Comores ---

    {
        "id": "Q_BAL_023",
        "axe": 1,
        "axe_label": "Existence",
        "question": "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines aux Comores ?",
        "country": "Comores",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 4 du document fournit une interdiction rigoureuse de la capture, la détention et la "
            "mise à mort des spécimens des espèces animales de la liste I, y compris les baleines (cétacés)."
        ),
        "relevant_keywords": ['interdit', 'baleine'],
    },

    {
        "id": "Q_BAL_024",
        "axe": 2,
        "axe_label": "Zonage",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines aux Comores qui "
            "précise que cette mesure n'est applicable qu'à certaines zones, aires ou régions ?"
        ),
        "country": "Comores",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas d'article portant sur l'interdiction spécifique des baleines dans certaines zones "
            "aux Comores."
        ),
        "relevant_keywords": ['zone', 'mammifère'],
    },

    {
        "id": "Q_BAL_025",
        "axe": 3,
        "axe_label": "Temporalité",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines aux Comores qui "
            "précise que cette mesure n'est pas applicable en permanence (temporalité) ?"
        ),
        "country": "Comores",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a aucun article portant sur l'interdiction de la chasse, pêche ou capture des baleines "
            "(cétacés) avec une temporalité spécifique aux Comores dans les documents fournis."
        ),
        "relevant_keywords": ['période', 'mammifère'],
    },

    {
        "id": "Q_BAL_026",
        "axe": 4,
        "axe_label": "Types d\'activités concernées",
        "question": (
            "Est-ce qu'un texte juridique précise les types d'activités concernées par l'interdiction de la "
            "chasse des baleines aux Comores ?"
        ),
        "country": "Comores",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 4 du document fournit une liste d'interdictions spécifiques pour les espèces animales "
            "de la liste I, y compris les baleines (cétacés) qui sont considérées comme des espèces protégées aux "
            "Comores."
        ),
        "relevant_keywords": ['capture', 'mammifère'],
    },

    {
        "id": "Q_BAL_027",
        "axe": 5,
        "axe_label": "Exceptions hors santé/ordre/recherche",
        "question": (
            "Est-ce qu'un texte juridique mentionne des exceptions à l'interdiction de la chasse des baleines aux "
            "Comores ? Vérifie si ce texte inclut des exceptions relatives à d'autres domaines que de la santé, "
            "de l'ordre public et de la recherche."
        ),
        "country": "Comores",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 9 permet des exceptions pour les espèces de la liste II, y compris les baleines "
            "(cétacés), si une autorisation préalable est obtenue auprès du ministre de l'environnement après un "
            "avis scientifique positif préalable."
        ),
        "relevant_keywords": [],
        "is_piege": True,
    },

    {
        "id": "Q_BAL_028",
        "axe": 6,
        "axe_label": "Exceptions / dérogations spécifiques",
        "question": (
            "Est-ce qu'un texte juridique mentionne des exceptions à l'interdiction de la chasse des baleines aux "
            "Comores ? Ne pas inclure les délais de mise en place de la loi. Les dérogations ou autorisations "
            "spécifiques constituent des exceptions."
        ),
        "country": "Comores",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 9 mentionne des exceptions à l'interdiction de capture et de pêche des baleines "
            "(cétacés) aux Comores, notamment pour les espèces de la liste II, sous réserve d'une autorisation "
            "préalable du ministre de l'environnement après avis scientifique positif préalable."
        ),
        "relevant_keywords": ['dérogation', 'mammifère'],
    },

    {
        "id": "Q_BAL_029",
        "axe": 7,
        "axe_label": "Sanction financière",
        "question": (
            "Est-ce qu'il existe un article qui précise que l'infraction à l'interdiction de la chasse des "
            "baleines aux Comores entraîne une sanction financière ?"
        ),
        "country": "Comores",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 12 précise que toute violation ou tentative de violation des dispositions ci-dessus "
            "sera punie conformément aux règles posées par la loi-cadre relative à l'environnement."
        ),
        "relevant_keywords": ['amende', 'baleine'],
    },

    {
        "id": "Q_BAL_030",
        "axe": 8,
        "axe_label": "Sanction pénale",
        "question": (
            "Est-ce que l'infraction à l'interdiction de la chasse des baleines aux Comores entraîne une peine de "
            "prison ?"
        ),
        "country": "Comores",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas de mention de peine de prison dans les articles fournis pour l'interdiction de la "
            "chasse, pêche ou capture des baleines (cétacés) aux Comores."
        ),
        "relevant_keywords": ['emprisonnement', 'baleine'],
    },

    {
        "id": "Q_BAL_031",
        "axe": 9,
        "axe_label": "Contrôle — acteurs institutionnels",
        "question": (
            "Est-ce que aux Comores, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction de la chasse des baleines ?"
        ),
        "country": "Comores",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, aux Comores, il existe des procédures de contrôle spécifiques pour garantir le respect de "
            "l'interdiction de la chasse, pêche ou capture des baleines (cétacés). L'article 4 de l'Arrêté n° "
            "01/031/MPE/CAB du 14/05/2001 portant protection des espèces de faune et flore sauvages des Comores "
            "interdit strictement la capture, la détention et la mise à mort des spécimens animaux, y compris les "
            "baleines. De plus, l'article 9 prévoit que toute opération menées à des fins d'étude et de recherche "
            "scientifique sur ces espèces doit être soumise à autorisation préalable du Ministre de "
            "l'environnement, après avis scientifique positif préalable."
        ),
        "relevant_keywords": ['administration', 'baleine'],
    },

    {
        "id": "Q_BAL_032",
        "axe": 10,
        "axe_label": "Contrôle — temporalité",
        "question": (
            "Est-ce que aux Comores, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction de la chasse des baleines ? Si ces procédures existent, "
            "vérifiez si elles précisent des périodes (temporalité) spécifiques pour le contrôle du respect de "
            "l'interdiction de la chasse des baleines."
        ),
        "country": "Comores",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Il n'y a pas de référence explicite dans les articles fournis à des procédures de contrôle "
            "spécifiques pour garantir ou assurer le respect de l'interdiction des baleines aux Comores."
        ),
        "relevant_keywords": ['période', 'baleine'],
    },

    {
        "id": "Q_BAL_033",
        "axe": 11,
        "axe_label": "Contrôle — zones",
        "question": (
            "Est-ce que aux Comores, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction de la chasse des baleines ? Si ces procédures existent, "
            "vérifiez si elles précisent des lieux ou zones spécifiques pour le contrôle du respect de "
            "l'interdiction de la chasse des baleines."
        ),
        "country": "Comores",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Les articles 10 et 73-75 de la loi-cadre relative à l'environnement sont applicables à la procédure "
            "de poursuite et de sanction des infractions aux dispositions relatives aux baleines (cétacés). "
            "Cependant, il n'y a pas de mention spécifique d'une administration, d'un comité ou d'un agent pour "
            "superviser le respect de l'interdiction."
        ),
        "relevant_keywords": ['zone', 'baleine'],
    },

    # --- Congo ---

    {
        "id": "Q_BAL_034",
        "axe": 1,
        "axe_label": "Existence",
        "question": "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines au Congo ?",
        "country": "Congo",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 14 de la loi n° 14/003 du 11 février 2014 relative à la conservation de la nature en "
            "République démocratique du Congo interdit la chasse, la pêche ou la capture des baleines (cétacés) "
            "considérées comme espèces protégées."
        ),
        "relevant_keywords": ['interdit', 'baleine'],
    },

    {
        "id": "Q_BAL_035",
        "axe": 2,
        "axe_label": "Zonage",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines au Congo qui "
            "précise que cette mesure n'est applicable qu'à certaines zones, aires ou régions ?"
        ),
        "country": "Congo",
        "theme": "chasse_baleines",
        "ground_truth": "Non.",
        "relevant_keywords": ['zone', 'mammifère'],
    },

    {
        "id": "Q_BAL_036",
        "axe": 3,
        "axe_label": "Temporalité",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines au Congo qui "
            "précise que cette mesure n'est pas applicable en permanence (temporalité) ?"
        ),
        "country": "Congo",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas d'article portant sur l'interdiction de la chasse, pêche ou capture des baleines "
            "(cétacés) avec une temporalité spécifique en République démocratique du Congo dans les documents "
            "fournis."
        ),
        "relevant_keywords": ['période', 'mammifère'],
    },

    {
        "id": "Q_BAL_037",
        "axe": 4,
        "axe_label": "Types d\'activités concernées",
        "question": (
            "Est-ce qu'un texte juridique précise les types d'activités concernées par l'interdiction de la "
            "chasse des baleines au Congo ?"
        ),
        "country": "Congo",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 13 précise que la protection concerne particulièrement les mammifères considérés "
            "comme menacés d'extinction ou susceptibles de l'être en République démocratique du Congo. Les "
            "baleines (cétacés) sont donc concernées par cette interdiction."
        ),
        "relevant_keywords": ['capture', 'mammifère'],
    },

    {
        "id": "Q_BAL_038",
        "axe": 5,
        "axe_label": "Exceptions hors santé/ordre/recherche",
        "question": (
            "Est-ce qu'un texte juridique mentionne des exceptions à l'interdiction de la chasse des baleines au "
            "Congo ? Vérifie si ce texte inclut des exceptions relatives à d'autres domaines que de la santé, de "
            "l'ordre public et de la recherche."
        ),
        "country": "Congo",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 20 prévoit des exceptions pour l'éducation, le repeuplement et la réintroduction "
            "d'espèces, ainsi que pour la recherche scientifique et la bioprospection."
        ),
        "relevant_keywords": [],
        "is_piege": True,
    },

    {
        "id": "Q_BAL_039",
        "axe": 6,
        "axe_label": "Exceptions / dérogations spécifiques",
        "question": (
            "Est-ce qu'un texte juridique mentionne des exceptions à l'interdiction de la chasse des baleines au "
            "Congo ? Ne pas inclure les délais de mise en place de la loi. Les dérogations ou autorisations "
            "spécifiques constituent des exceptions."
        ),
        "country": "Congo",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 20 de la loi n°14/003 du 11 février 2014 relative à la conservation de la nature "
            "prévoit des dérogations pour la protection de la faune et de la flore sauvages, y compris dans les "
            "aires protégées gérées par un organisme public. Ces dérogations peuvent être accordées dans "
            "l'intérêt de la santé et de la sécurité publique, ainsi que de la sécurité alimentaire des "
            "populations riveraines des aires protégées, pour prévenir des dommages importants notamment aux "
            "cultures, à l'élevage, aux forêts, aux pêcheries, aux eaux et à d'autres formes de propriété, à des "
            "fins d'éducation, de repeuplement et de réintroduction de ces espèces et pour des opérations de "
            "reproduction nécessaires à ces fins, y compris la propagation artificielle des plantes, ainsi que "
            "pour des fins de recherche scientifique et de bioprospection."
        ),
        "relevant_keywords": ['dérogation', 'mammifère'],
    },

    {
        "id": "Q_BAL_040",
        "axe": 7,
        "axe_label": "Sanction financière",
        "question": (
            "Est-ce qu'il existe un article qui précise que l'infraction à l'interdiction de la chasse des "
            "baleines au Congo entraîne une sanction financière ?"
        ),
        "country": "Congo",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 78 précise que la chasse, la pêche ou la capture de spécimens d'une espèce de faune "
            "sauvage intégralement protégée entraîne une amende de cinq millions à vingt millions de francs "
            "congolais."
        ),
        "relevant_keywords": ['amende', 'baleine'],
    },

    {
        "id": "Q_BAL_041",
        "axe": 8,
        "axe_label": "Sanction pénale",
        "question": (
            "Est-ce que l'infraction à l'interdiction de la chasse des baleines au Congo entraîne une peine de "
            "prison ?"
        ),
        "country": "Congo",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'infraction à l'interdiction de la chasse, pêche ou capture des baleines (cétacés) en "
            "République démocratique du Congo entraîne une peine de prison selon l'article 72 de la loi n° 14/003 "
            "du 11 février 2014 relative à la conservation de la nature."
        ),
        "relevant_keywords": ['emprisonnement', 'baleine'],
    },

    {
        "id": "Q_BAL_042",
        "axe": 9,
        "axe_label": "Contrôle — acteurs institutionnels",
        "question": (
            "Est-ce que au Congo, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction de la chasse des baleines ?"
        ),
        "country": "Congo",
        "theme": "chasse_baleines",
        "ground_truth": (
            "L'article 14 de la loi n° 14/003 du 11 février 2014 relative à la conservation de la nature interdit "
            "la chasse, la pêche ou la capture des baleines (cétacés) en République démocratique du Congo."
        ),
        "relevant_keywords": ['administration', 'baleine'],
    },

    {
        "id": "Q_BAL_043",
        "axe": 10,
        "axe_label": "Contrôle — temporalité",
        "question": (
            "Est-ce que au Congo, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction de la chasse des baleines ? Si ces procédures existent, "
            "vérifiez si elles précisent des périodes (temporalité) spécifiques pour le contrôle du respect de "
            "l'interdiction de la chasse des baleines."
        ),
        "country": "Congo",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas de procédures de contrôle spécifiquement décrites dans les articles fournis pour "
            "garantir ou assurer le respect de l'interdiction des baleines (cétacés) en République démocratique "
            "du Congo."
        ),
        "relevant_keywords": ['période', 'baleine'],
    },

    {
        "id": "Q_BAL_044",
        "axe": 11,
        "axe_label": "Contrôle — zones",
        "question": (
            "Est-ce que au Congo, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction de la chasse des baleines ? Si ces procédures existent, "
            "vérifiez si elles précisent des lieux ou zones spécifiques pour le contrôle du respect de "
            "l'interdiction de la chasse des baleines."
        ),
        "country": "Congo",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Je n'ai pas trouvé d'informations spécifiques sur des procédures de contrôle visant à garantir ou "
            "assurer le respect de l'interdiction des baleines (cétacés) dans la République démocratique du "
            "Congo. Les documents fournis ne mentionnent pas expressément une administration, un comité, un "
            "service ou un agent chargé de superviser, évaluer ou constater l'application de cette interdiction."
        ),
        "relevant_keywords": ['zone', 'baleine'],
    },

    # --- Djibouti ---

    {
        "id": "Q_BAL_045",
        "axe": 1,
        "axe_label": "Existence",
        "question": "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines à Djibouti ?",
        "country": "Djibouti",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'ARTICLE 3 interdit la chasse, le commerce et l'esportation des mammifères marins, notamment "
            "les baleines (cétacés), dans l'ensemble du territoire marin et terrestre de la République de "
            "Djibouti."
        ),
        "relevant_keywords": ['interdit', 'baleine'],
    },

    {
        "id": "Q_BAL_046",
        "axe": 2,
        "axe_label": "Zonage",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines à Djibouti qui "
            "précise que cette mesure n'est applicable qu'à certaines zones, aires ou régions ?"
        ),
        "country": "Djibouti",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas d'article portant sur l'interdiction des baleines (cétacés) qui précise que cette "
            "mesure n'est applicable qu'à certaines zones, aires ou régions à Djibouti."
        ),
        "relevant_keywords": ['zone', 'mammifère'],
    },

    {
        "id": "Q_BAL_047",
        "axe": 3,
        "axe_label": "Temporalité",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines à Djibouti qui "
            "précise que cette mesure n'est pas applicable en permanence (temporalité) ?"
        ),
        "country": "Djibouti",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas d'article portant sur l'interdiction des baleines (cétacés) à Djibouti qui précise "
            "que cette mesure n'est pas applicable en permanence."
        ),
        "relevant_keywords": ['période', 'mammifère'],
    },

    {
        "id": "Q_BAL_048",
        "axe": 4,
        "axe_label": "Types d\'activités concernées",
        "question": (
            "Est-ce qu'un texte juridique précise les types d'activités concernées par l'interdiction de la "
            "chasse des baleines à Djibouti ?"
        ),
        "country": "Djibouti",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 3 précise que la chasse, le commerce et l'exportation des mammifères marins, "
            "notamment les dauphins, cachalots, dugongs et tortues marines et terrestres sont interdits dans "
            "l'ensemble du territoire marin et terrestre de la République de Djibouti."
        ),
        "relevant_keywords": ['capture', 'mammifère'],
    },

    {
        "id": "Q_BAL_049",
        "axe": 5,
        "axe_label": "Exceptions hors santé/ordre/recherche",
        "question": (
            "Est-ce qu'un texte juridique mentionne des exceptions à l'interdiction de la chasse des baleines à "
            "Djibouti ? Vérifie si ce texte inclut des exceptions relatives à d'autres domaines que de la santé, "
            "de l'ordre public et de la recherche."
        ),
        "country": "Djibouti",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas d'exceptions mentionnées dans ces articles juridiques pour l'interdiction de la "
            "chasse, de la pêche ou de la capture des baleines (cétacés) à Djibouti."
        ),
        "relevant_keywords": [],
        "is_piege": True,
    },

    {
        "id": "Q_BAL_050",
        "axe": 6,
        "axe_label": "Exceptions / dérogations spécifiques",
        "question": (
            "Est-ce qu'un texte juridique mentionne des exceptions à l'interdiction de la chasse des baleines à "
            "Djibouti ? Ne pas inclure les délais de mise en place de la loi. Les dérogations ou autorisations "
            "spécifiques constituent des exceptions."
        ),
        "country": "Djibouti",
        "theme": "chasse_baleines",
        "ground_truth": "Oui, l'article 9 autorise les pêches et collectes à titre scientifique sous contrôle de l'ISERST.",
        "relevant_keywords": ['dérogation', 'mammifère'],
    },

    {
        "id": "Q_BAL_051",
        "axe": 7,
        "axe_label": "Sanction financière",
        "question": (
            "Est-ce qu'il existe un article qui précise que l'infraction à l'interdiction de la chasse des "
            "baleines à Djibouti entraîne une sanction financière ?"
        ),
        "country": "Djibouti",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 11 précise que les infractions au décret seront punies d'une amende de 4e catégorie "
            "(300.000 FD à 2.000.000 FD)."
        ),
        "relevant_keywords": ['amende', 'baleine'],
    },

    {
        "id": "Q_BAL_052",
        "axe": 8,
        "axe_label": "Sanction pénale",
        "question": (
            "Est-ce que l'infraction à l'interdiction de la chasse des baleines à Djibouti entraîne une peine de "
            "prison ?"
        ),
        "country": "Djibouti",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'infraction à l'interdiction de la chasse, du commerce et de l'exportation des mammifères "
            "marins (dont les baleines) entraîne une peine de prison en cas de récidive selon l'ARTICLE 11 du "
            "décret nº 85-103/PR/AG de la République de Djibouti."
        ),
        "relevant_keywords": ['emprisonnement', 'baleine'],
    },

    {
        "id": "Q_BAL_053",
        "axe": 9,
        "axe_label": "Contrôle — acteurs institutionnels",
        "question": (
            "Est-ce que à Djibouti, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction de la chasse des baleines ?"
        ),
        "country": "Djibouti",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'Article 10 du décret nº 85-103/PR/AG habilite plusieurs personnes et leurs représentants "
            "désignés à constater les infractions au présent décret, y compris les officiers de police judiciaire "
            "et le directeur de l'ISERST."
        ),
        "relevant_keywords": ['administration', 'baleine'],
    },

    {
        "id": "Q_BAL_054",
        "axe": 10,
        "axe_label": "Contrôle — temporalité",
        "question": (
            "Est-ce que à Djibouti, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction de la chasse des baleines ? Si ces procédures existent, "
            "vérifiez si elles précisent des périodes (temporalité) spécifiques pour le contrôle du respect de "
            "l'interdiction de la chasse des baleines."
        ),
        "country": "Djibouti",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'ARTICLE 10 habilite plusieurs personnes à constater les infractions au décret. Il n'y a pas "
            "d'informations sur les périodes spécifiques pour les contrôles dans le contexte fourni."
        ),
        "relevant_keywords": ['période', 'baleine'],
    },

    {
        "id": "Q_BAL_055",
        "axe": 11,
        "axe_label": "Contrôle — zones",
        "question": (
            "Est-ce que à Djibouti, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction de la chasse des baleines ? Si ces procédures existent, "
            "vérifiez si elles précisent des lieux ou zones spécifiques pour le contrôle du respect de "
            "l'interdiction de la chasse des baleines."
        ),
        "country": "Djibouti",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas d'informations dans les articles juridiques fournis concernant des procédures de "
            "surveillance et de contrôle spécifiques à Djibouti pour garantir le respect de l'interdiction de la "
            "chasse ou de la pêche illégale de baleines et autres cétacés. Les articles se concentrent "
            "principalement sur les interdictions elles-mêmes et sur les personnes habilitées à constater les "
            "infractions."
        ),
        "relevant_keywords": ['zone', 'baleine'],
    },

    # --- Gabon ---

    {
        "id": "Q_BAL_056",
        "axe": 1,
        "axe_label": "Existence",
        "question": "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines au Gabon ?",
        "country": "Gabon",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 6 stipule que les baleines (cétacés), étant des espèces indiquées à l'article 5, ne "
            "peuvent être chassées ou capturées sous réserve des dispositions relatives à la légitime défense et "
            "aux battues administratives pour assurer la protection des personnes et des biens ou encore aux "
            "repeuplements et prélèvements à des fins scientifiques."
        ),
        "relevant_keywords": ['interdit', 'baleine'],
    },

    {
        "id": "Q_BAL_057",
        "axe": 2,
        "axe_label": "Zonage",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines au Gabon qui "
            "précise que cette mesure n'est applicable qu'à certaines zones, aires ou régions ?"
        ),
        "country": "Gabon",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas un article portant sur l'interdiction des baleines (cétacés) (chasse, pêche ou "
            "capture) qui précise que cette mesure n'est applicable qu'à certaines zones, aires ou régions au "
            "Gabon dans le contexte fourni."
        ),
        "relevant_keywords": ['zone', 'mammifère'],
    },

    {
        "id": "Q_BAL_058",
        "axe": 3,
        "axe_label": "Temporalité",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines au Gabon qui "
            "précise que cette mesure n'est pas applicable en permanence (temporalité) ?"
        ),
        "country": "Gabon",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas d'article portant sur l'interdiction des baleines (cétacés) qui précise que cette "
            "mesure n'est pas applicable en permanence au Gabon dans le contexte fourni."
        ),
        "relevant_keywords": ['période', 'mammifère'],
    },

    {
        "id": "Q_BAL_059",
        "axe": 4,
        "axe_label": "Types d\'activités concernées",
        "question": (
            "Est-ce qu'un texte juridique précise les types d'activités concernées par l'interdiction de la "
            "chasse des baleines au Gabon ?"
        ),
        "country": "Gabon",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 5 du Décret n. 0040bisPR/MEFPECCHF portant classement des espèces animales sauvages "
            "au Gabon classe les baleines et autres cétacés dans la catégorie des espèces animales intégralement "
            "protégées, interdisant ainsi leur chasse ou exploitation."
        ),
        "relevant_keywords": ['capture', 'mammifère'],
    },

    {
        "id": "Q_BAL_060",
        "axe": 5,
        "axe_label": "Exceptions hors santé/ordre/recherche",
        "question": (
            "Est-ce qu'un texte juridique mentionne des exceptions à l'interdiction de la chasse des baleines au "
            "Gabon ? Vérifie si ce texte inclut des exceptions relatives à d'autres domaines que de la santé, de "
            "l'ordre public et de la recherche."
        ),
        "country": "Gabon",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas d'exceptions mentionnées dans ces articles juridiques pour l'interdiction de "
            "chasse, pêche ou capture des baleines (cétacés) au Gabon."
        ),
        "relevant_keywords": [],
        "is_piege": True,
    },

    {
        "id": "Q_BAL_061",
        "axe": 6,
        "axe_label": "Exceptions / dérogations spécifiques",
        "question": (
            "Est-ce qu'un texte juridique mentionne des exceptions à l'interdiction de la chasse des baleines au "
            "Gabon ? Ne pas inclure les délais de mise en place de la loi. Les dérogations ou autorisations "
            "spécifiques constituent des exceptions."
        ),
        "country": "Gabon",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 6 mentionne une exception pour la chasse ou capture des baleines (cétacés) dans "
            "certaines conditions, notamment pour la légitime défense et les repeuplements à des fins "
            "scientifiques."
        ),
        "relevant_keywords": ['dérogation', 'mammifère'],
    },

    {
        "id": "Q_BAL_062",
        "axe": 7,
        "axe_label": "Sanction financière",
        "question": (
            "Est-ce qu'il existe un article qui précise que l'infraction à l'interdiction de la chasse des "
            "baleines au Gabon entraîne une sanction financière ?"
        ),
        "country": "Gabon",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas d'article dans le contexte qui précise que l'infraction à l'interdiction des "
            "baleines (cétacés) au Gabon entraîne une sanction financière."
        ),
        "relevant_keywords": ['amende', 'baleine'],
    },

    {
        "id": "Q_BAL_063",
        "axe": 8,
        "axe_label": "Sanction pénale",
        "question": (
            "Est-ce que l'infraction à l'interdiction de la chasse des baleines au Gabon entraîne une peine de "
            "prison ?"
        ),
        "country": "Gabon",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas de mention de peine de prison dans les articles fournis pour l'infraction à "
            "l'interdiction de chasse ou de capture des baleines au Gabon."
        ),
        "relevant_keywords": ['emprisonnement', 'baleine'],
    },

    {
        "id": "Q_BAL_064",
        "axe": 9,
        "axe_label": "Contrôle — acteurs institutionnels",
        "question": (
            "Est-ce que au Gabon, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction de la chasse des baleines ?"
        ),
        "country": "Gabon",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Il n'y a pas d'articles juridiques dans le contexte, donc je ne peux pas répondre à la question "
            "basée sur les informations données."
        ),
        "relevant_keywords": ['administration', 'baleine'],
    },

    {
        "id": "Q_BAL_065",
        "axe": 10,
        "axe_label": "Contrôle — temporalité",
        "question": (
            "Est-ce que au Gabon, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction de la chasse des baleines ? Si ces procédures existent, "
            "vérifiez si elles précisent des périodes (temporalité) spécifiques pour le contrôle du respect de "
            "l'interdiction de la chasse des baleines."
        ),
        "country": "Gabon",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Il n'y a pas d'informations concernant des procédures de contrôle spécifiques dans les documents "
            "fournis."
        ),
        "relevant_keywords": ['période', 'baleine'],
    },

    {
        "id": "Q_BAL_066",
        "axe": 11,
        "axe_label": "Contrôle — zones",
        "question": (
            "Est-ce que au Gabon, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction de la chasse des baleines ? Si ces procédures existent, "
            "vérifiez si elles précisent des lieux ou zones spécifiques pour le contrôle du respect de "
            "l'interdiction de la chasse des baleines."
        ),
        "country": "Gabon",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas de procédures de contrôle spécifiquement décrites dans les articles fournis pour "
            "garantir ou assurer le respect de l'interdiction des baleines au Gabon."
        ),
        "relevant_keywords": ['zone', 'baleine'],
    },

    # --- Guinée ---

    {
        "id": "Q_BAL_067",
        "axe": 1,
        "axe_label": "Existence",
        "question": "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines en Guinée ?",
        "country": "Guinée",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 85 interdit la chasse, la capture et la pêche des baleines (cétacés) dans les zones "
            "maritimes sous souveraineté ou juridiction guinéenne."
        ),
        "relevant_keywords": ['interdit', 'baleine'],
    },

    {
        "id": "Q_BAL_068",
        "axe": 2,
        "axe_label": "Zonage",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines en Guinée qui "
            "précise que cette mesure n'est applicable qu'à certaines zones, aires ou régions ?"
        ),
        "country": "Guinée",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas d'article portant sur l'interdiction des baleines (cétacés) qui précise que cette "
            "mesure n'est applicable qu'à certaines zones, aires ou régions en Guinée dans les documents fournis."
        ),
        "relevant_keywords": ['zone', 'mammifère'],
    },

    {
        "id": "Q_BAL_069",
        "axe": 3,
        "axe_label": "Temporalité",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines en Guinée qui "
            "précise que cette mesure n'est pas applicable en permanence (temporalité) ?"
        ),
        "country": "Guinée",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas d'article portant sur l'interdiction de la chasse, pêche ou capture des baleines "
            "(cétacés) avec une temporalité spécifique en Guinée dans les articles fournis."
        ),
        "relevant_keywords": ['période', 'mammifère'],
    },

    {
        "id": "Q_BAL_070",
        "axe": 4,
        "axe_label": "Types d\'activités concernées",
        "question": (
            "Est-ce qu'un texte juridique précise les types d'activités concernées par l'interdiction de la "
            "chasse des baleines en Guinée ?"
        ),
        "country": "Guinée",
        "theme": "chasse_baleines",
        "ground_truth": (
            "L'article 85 du Code de la pêche maritime guinéen interdit \"de tuer, de mutiler, de capturer, "
            "d'enlever ou de chasser\" les baleines (cétacés) dans les zones maritimes sous souveraineté ou "
            "juridiction guinéenne."
        ),
        "relevant_keywords": ['capture', 'mammifère'],
    },

    {
        "id": "Q_BAL_071",
        "axe": 5,
        "axe_label": "Exceptions hors santé/ordre/recherche",
        "question": (
            "Est-ce qu'un texte juridique mentionne des exceptions à l'interdiction de la chasse des baleines en "
            "Guinée ? Vérifie si ce texte inclut des exceptions relatives à d'autres domaines que de la santé, de "
            "l'ordre public et de la recherche."
        ),
        "country": "Guinée",
        "theme": "chasse_baleines",
        "ground_truth": "Il y a l'exception scientifique (article 58)",
        "relevant_keywords": [],
        "is_piege": True,
    },

    {
        "id": "Q_BAL_072",
        "axe": 6,
        "axe_label": "Exceptions / dérogations spécifiques",
        "question": (
            "Est-ce qu'un texte juridique mentionne des exceptions à l'interdiction de la chasse des baleines en "
            "Guinée ? Ne pas inclure les délais de mise en place de la loi. Les dérogations ou autorisations "
            "spécifiques constituent des exceptions."
        ),
        "country": "Guinée",
        "theme": "chasse_baleines",
        "ground_truth": "Il y a l'exception scientifique (article 58)",
        "relevant_keywords": ['dérogation', 'mammifère'],
    },

    {
        "id": "Q_BAL_073",
        "axe": 7,
        "axe_label": "Sanction financière",
        "question": (
            "Est-ce qu'il existe un article qui précise que l'infraction à l'interdiction de la chasse des "
            "baleines en Guinée entraîne une sanction financière ?"
        ),
        "country": "Guinée",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 85 interdit de tuer, mutiler, capturer, enlever ou chasser des baleines et autres "
            "espèces marines protégées dans les zones maritimes sous souveraineté ou juridiction guinéenne. La "
            "violation de cette interdiction est considérée comme une infraction très grave conformément aux "
            "articles 234 et 238."
        ),
        "relevant_keywords": ['amende', 'baleine'],
    },

    {
        "id": "Q_BAL_074",
        "axe": 8,
        "axe_label": "Sanction pénale",
        "question": (
            "Est-ce que l'infraction à l'interdiction de la chasse des baleines en Guinée entraîne une peine de "
            "prison ?"
        ),
        "country": "Guinée",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'infraction à l'interdiction de la chasse, pêche ou capture des baleines (cétacés) en Guinée "
            "entraîne une peine de prison. Selon l'article 164 du Code de protection de la faune sauvage et "
            "réglementation de la chasse guinéen, quiconque abat ou capture des animaux partiellement protégés en "
            "excédant les latitudes d'abattage ou de capture est puni d'un emprisonnement de 6 mois à 1 an et "
            "d'une amende de 10 000 000 GNF à 30 000 000 GNF."
        ),
        "relevant_keywords": ['emprisonnement', 'baleine'],
    },

    {
        "id": "Q_BAL_075",
        "axe": 9,
        "axe_label": "Contrôle — acteurs institutionnels",
        "question": (
            "Est-ce que en Guinée, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction de la chasse des baleines ?"
        ),
        "country": "Guinée",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, il existe des procédures spécifiques de contrôle pour garantir le respect de l'interdiction de "
            "la chasse, pêche ou capture de baleines (cétacés) et autres mammifères marins protégés en Guinée. "
            "L'article 85 du Code de la pêche maritime interdit toute killings, mutilations, captures, "
            "enlèvements ou chasses de ces espèces marines protégées dans les zones maritimes sous souveraineté "
            "ou juridiction guinéenne. Le Ministère chargé de la Pêche Maritime assure le contrôle sur le "
            "territoire guinéen de l'application des règles du présent Code et des règlements pris pour son "
            "application à tous les stades de la commercialisation des produits issus de la pêche maritime, de la "
            "première vente à la vente au détail, y compris le transport (article 144)."
        ),
        "relevant_keywords": ['administration', 'baleine'],
    },

    {
        "id": "Q_BAL_076",
        "axe": 10,
        "axe_label": "Contrôle — temporalité",
        "question": (
            "Est-ce que en Guinée, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction de la chasse des baleines ? Si ces procédures existent, "
            "vérifiez si elles précisent des périodes (temporalité) spécifiques pour le contrôle du respect de "
            "l'interdiction de la chasse des baleines."
        ),
        "country": "Guinée",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Il n'y a pas de mention explicite de procédures de contrôle spécifiques pour garantir ou assurer le "
            "respect de l'interdiction des baleines (cétacés) dans les articles juridiques fournis. Cependant, il "
            "est mentionné que toute action ou toute tentative d'action d'une activité connexe à la pêche "
            "commerciale, sans autorisation, constitue une infraction très grave (Article 64). Il est donc "
            "possible que ces procédures de contrôle soient incluses dans les réglementations générales relatives "
            "aux activités de pêche et non spécifiquement mentionnées pour les baleines."
        ),
        "relevant_keywords": ['période', 'baleine'],
    },

    {
        "id": "Q_BAL_077",
        "axe": 11,
        "axe_label": "Contrôle — zones",
        "question": (
            "Est-ce que en Guinée, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction de la chasse des baleines ? Si ces procédures existent, "
            "vérifiez si elles précisent des lieux ou zones spécifiques pour le contrôle du respect de "
            "l'interdiction de la chasse des baleines."
        ),
        "country": "Guinée",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Il n'y a pas de mention explicite dans les articles juridiques fournis concernant des procédures de "
            "contrôle spécifiques pour garantir ou assurer le respect de l'interdiction des baleines (cétacés) en "
            "Guinée. Les articles se concentrent principalement sur l'interdiction générale de la pêche et des "
            "activités connexes, y compris celle concernant les espèces marines protégées et menacées. Il n'y a "
            "pas non plus de précision sur des lieux ou zones spécifiques pour le contrôle du respect de "
            "l'interdiction des baleines (cétacés)."
        ),
        "relevant_keywords": ['zone', 'baleine'],
    },

    # --- Madagascar ---

    {
        "id": "Q_BAL_078",
        "axe": 1,
        "axe_label": "Existence",
        "question": "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines à Madagascar ?",
        "country": "Madagascar",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 18 interdit la chasse, la pêche et la capture de toutes les espèces menacées et "
            "protégées, y compris les baleines (cétacés)."
        ),
        "relevant_keywords": ['interdit', 'baleine'],
    },

    {
        "id": "Q_BAL_079",
        "axe": 2,
        "axe_label": "Zonage",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines à Madagascar qui "
            "précise que cette mesure n'est applicable qu'à certaines zones, aires ou régions ?"
        ),
        "country": "Madagascar",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas d'article spécifique mentionnant une interdiction de la chasse, pêche ou capture "
            "des baleines applicable uniquement dans certaines zones spécifiques du pays à Madagascar."
        ),
        "relevant_keywords": ['zone', 'mammifère'],
    },

    {
        "id": "Q_BAL_080",
        "axe": 3,
        "axe_label": "Temporalité",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines à Madagascar qui "
            "précise que cette mesure n'est pas applicable en permanence (temporalité) ?"
        ),
        "country": "Madagascar",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas d'article portant sur l'interdiction des baleines (cétacés) à Madagascar qui "
            "précise une temporalité spécifique pour cette interdiction."
        ),
        "relevant_keywords": ['période', 'mammifère'],
    },

    {
        "id": "Q_BAL_081",
        "axe": 4,
        "axe_label": "Types d\'activités concernées",
        "question": (
            "Est-ce qu'un texte juridique précise les types d'activités concernées par l'interdiction de la "
            "chasse des baleines à Madagascar ?"
        ),
        "country": "Madagascar",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 18 précise que la pêche, la capture, la détention et la commercialisation de toutes "
            "les espèces menacées et protégées sont interdites, y compris les baleines (cétacés)."
        ),
        "relevant_keywords": ['capture', 'mammifère'],
    },

    {
        "id": "Q_BAL_082",
        "axe": 5,
        "axe_label": "Exceptions hors santé/ordre/recherche",
        "question": (
            "Est-ce qu'un texte juridique mentionne des exceptions à l'interdiction de la chasse des baleines à "
            "Madagascar ? Vérifie si ce texte inclut des exceptions relatives à d'autres domaines que de la "
            "santé, de l'ordre public et de la recherche."
        ),
        "country": "Madagascar",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas d'exceptions mentionnées dans les articles juridiques fournis concernant "
            "l'interdiction de la pêche, capture et commercialisation de baleines (cétacés) à Madagascar."
        ),
        "relevant_keywords": [],
        "is_piege": True,
    },

    {
        "id": "Q_BAL_083",
        "axe": 6,
        "axe_label": "Exceptions / dérogations spécifiques",
        "question": (
            "Est-ce qu'un texte juridique mentionne des exceptions à l'interdiction de la chasse des baleines à "
            "Madagascar ? Ne pas inclure les délais de mise en place de la loi. Les dérogations ou autorisations "
            "spécifiques constituent des exceptions."
        ),
        "country": "Madagascar",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas d'exceptions mentionnées dans les articles juridiques fournis pour l'interdiction "
            "de la chasse, pêche ou capture des baleines (cétacés) à Madagascar."
        ),
        "relevant_keywords": ['dérogation', 'mammifère'],
    },

    {
        "id": "Q_BAL_084",
        "axe": 7,
        "axe_label": "Sanction financière",
        "question": (
            "Est-ce qu'il existe un article qui précise que l'infraction à l'interdiction de la chasse des "
            "baleines à Madagascar entraîne une sanction financière ?"
        ),
        "country": "Madagascar",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 88 précise que quiconque pêche, capture, transporte, détruit, détient ou "
            "commercialise toutes espèces menacées d'extinction et protégées, coraux, mammifères marins, oiseaux "
            "de mer, tortues marines et d’eau douce et/ou d'organismes aquatiques inscrites sur la liste établie "
            "par voie réglementaire est puni d’une amende de 10.000$ à 20.000$ et/ou d'une peine d'emprisonnement "
            "de six (6) à douze (12) mois."
        ),
        "relevant_keywords": ['amende', 'baleine'],
    },

    {
        "id": "Q_BAL_085",
        "axe": 8,
        "axe_label": "Sanction pénale",
        "question": (
            "Est-ce que l'infraction à l'interdiction de la chasse des baleines à Madagascar entraîne une peine "
            "de prison ?"
        ),
        "country": "Madagascar",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 88 prévoit une peine d'emprisonnement de six (6) à douze (12) mois pour quiconque "
            "pêche, capture, transporte, détruit, détient ou commercialise des baleines (cétacés)."
        ),
        "relevant_keywords": ['emprisonnement', 'baleine'],
    },

    {
        "id": "Q_BAL_086",
        "axe": 9,
        "axe_label": "Contrôle — acteurs institutionnels",
        "question": (
            "Est-ce que à Madagascar, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction de la chasse des baleines ?"
        ),
        "country": "Madagascar",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 64 décrit la responsabilité du Ministère en charge de la Pêche et de l'aquaculture "
            "dans la coordination des opérations de suivi, de contrôle et de surveillance des activités de pêche "
            "sur le territoire malagasy, y compris les mammifères marins protégés."
        ),
        "relevant_keywords": ['administration', 'baleine'],
    },

    {
        "id": "Q_BAL_087",
        "axe": 10,
        "axe_label": "Contrôle — temporalité",
        "question": (
            "Est-ce que à Madagascar, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction de la chasse des baleines ? Si ces procédures existent, "
            "vérifiez si elles précisent des périodes (temporalité) spécifiques pour le contrôle du respect de "
            "l'interdiction de la chasse des baleines."
        ),
        "country": "Madagascar",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, il existe une administration spécifique chargée de superviser et contrôler le respect de "
            "l'interdiction de la pêche des baleines à Madagascar. L'article 64 de la loi malgache portant Code "
            "de la pêche et de l'aquaculture stipule que le Ministère en charge de la Pêche et de l'aquaculture "
            "est responsable de la coordination des opérations de suivi, de contrôle et de surveillance des "
            "activités de pêche sur le territoire malagasy."
        ),
        "relevant_keywords": ['période', 'baleine'],
    },

    {
        "id": "Q_BAL_088",
        "axe": 11,
        "axe_label": "Contrôle — zones",
        "question": (
            "Est-ce que à Madagascar, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction de la chasse des baleines ? Si ces procédures existent, "
            "vérifiez si elles précisent des lieux ou zones spécifiques pour le contrôle du respect de "
            "l'interdiction de la chasse des baleines."
        ),
        "country": "Madagascar",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 64 décrit la responsabilité du Ministère en charge de la Pêche et de l'aquaculture "
            "dans la coordination des opérations de suivi, de contrôle et de surveillance des activités de pêche "
            "sur le territoire malagasy, y compris les eaux visées à l’article 3."
        ),
        "relevant_keywords": ['zone', 'baleine'],
    },

    # --- Mauritanie ---

    {
        "id": "Q_BAL_089",
        "axe": 1,
        "axe_label": "Existence",
        "question": "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines en Mauritanie ?",
        "country": "Mauritanie",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 39 interdit la chasse, la pêche et la détention de toutes les espèces de mammifères "
            "marins, y compris les baleines (cétacés), en Mauritanie."
        ),
        "relevant_keywords": ['interdit', 'baleine'],
    },

    {
        "id": "Q_BAL_090",
        "axe": 2,
        "axe_label": "Zonage",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines en Mauritanie "
            "qui précise que cette mesure n'est applicable qu'à certaines zones, aires ou régions ?"
        ),
        "country": "Mauritanie",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas d'article portant sur l'interdiction spécifique des baleines (cétacés) qui précise "
            "que cette mesure est applicable uniquement à certaines zones, aires ou régions en Mauritanie."
        ),
        "relevant_keywords": ['zone', 'mammifère'],
    },

    {
        "id": "Q_BAL_091",
        "axe": 3,
        "axe_label": "Temporalité",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines en Mauritanie "
            "qui précise que cette mesure n'est pas applicable en permanence (temporalité) ?"
        ),
        "country": "Mauritanie",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas d'article portant sur l'interdiction des baleines (cétacés) qui précise que cette "
            "mesure n'est pas applicable en permanence en Mauritanie dans les documents fournis."
        ),
        "relevant_keywords": ['période', 'mammifère'],
    },

    {
        "id": "Q_BAL_092",
        "axe": 4,
        "axe_label": "Types d\'activités concernées",
        "question": (
            "Est-ce qu'un texte juridique précise les types d'activités concernées par l'interdiction de la "
            "chasse des baleines en Mauritanie ?"
        ),
        "country": "Mauritanie",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 39 précise que la pêche, la capture et la détention de toutes espèces de mammifères "
            "marins sont interdites en tout temps et en tout lieu, sauf autorisation spéciale du ministre chargé "
            "des pêches et à des fins de recherche scientifique ou technique."
        ),
        "relevant_keywords": ['capture', 'mammifère'],
    },

    {
        "id": "Q_BAL_093",
        "axe": 5,
        "axe_label": "Exceptions hors santé/ordre/recherche",
        "question": (
            "Est-ce qu'un texte juridique mentionne des exceptions à l'interdiction de la chasse des baleines en "
            "Mauritanie ? Vérifie si ce texte inclut des exceptions relatives à d'autres domaines que de la "
            "santé, de l'ordre public et de la recherche."
        ),
        "country": "Mauritanie",
        "theme": "chasse_baleines",
        "ground_truth": "Il y a des exceptions scientifiques et techniques (article 39)",
        "relevant_keywords": [],
        "is_piege": True,
    },

    {
        "id": "Q_BAL_094",
        "axe": 6,
        "axe_label": "Exceptions / dérogations spécifiques",
        "question": (
            "Est-ce qu'un texte juridique mentionne des exceptions à l'interdiction de la chasse des baleines en "
            "Mauritanie ? Ne pas inclure les délais de mise en place de la loi. Les dérogations ou autorisations "
            "spécifiques constituent des exceptions."
        ),
        "country": "Mauritanie",
        "theme": "chasse_baleines",
        "ground_truth": "Il y a des exceptions scientifiques et techniques (article 39)",
        "relevant_keywords": ['dérogation', 'mammifère'],
    },

    {
        "id": "Q_BAL_095",
        "axe": 7,
        "axe_label": "Sanction financière",
        "question": (
            "Est-ce qu'il existe un article qui précise que l'infraction à l'interdiction de la chasse des "
            "baleines en Mauritanie entraîne une sanction financière ?"
        ),
        "country": "Mauritanie",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 83 de la loi mauritanienne portant code des pêches maritimes traite spécifiquement "
            "des sanctions financières pour les navires étrangers ayant entrepris des opérations de pêche sans y "
            "avoir été dûment autorisés. Cependant, cet article ne mentionne pas expressément l'interdiction de "
            "la chasse ou de la capture des baleines (cétacés) en Mauritanie."
        ),
        "relevant_keywords": ['amende', 'baleine'],
    },

    {
        "id": "Q_BAL_096",
        "axe": 8,
        "axe_label": "Sanction pénale",
        "question": (
            "Est-ce que l'infraction à l'interdiction de la chasse des baleines en Mauritanie entraîne une peine "
            "de prison ?"
        ),
        "country": "Mauritanie",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas mention d'une peine de prison pour l'infraction à l'interdiction de la chasse, "
            "pêche ou capture des baleines (cétacés) en Mauritanie dans les articles fournis."
        ),
        "relevant_keywords": ['emprisonnement', 'baleine'],
    },

    {
        "id": "Q_BAL_097",
        "axe": 9,
        "axe_label": "Contrôle — acteurs institutionnels",
        "question": (
            "Est-ce que en Mauritanie, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction de la chasse des baleines ?"
        ),
        "country": "Mauritanie",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 60 stipule que le ministre chargé des pêches est responsable de la coordination des "
            "opérations de contrôle et de surveillance des pêcheries dans les eaux sous juridiction "
            "mauritanienne, y compris pour assurer l'application et le respect des dispositions relatives aux "
            "mammifères marins protégés."
        ),
        "relevant_keywords": ['administration', 'baleine'],
    },

    {
        "id": "Q_BAL_098",
        "axe": 10,
        "axe_label": "Contrôle — temporalité",
        "question": (
            "Est-ce que en Mauritanie, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction de la chasse des baleines ? Si ces procédures existent, "
            "vérifiez si elles précisent des périodes (temporalité) spécifiques pour le contrôle du respect de "
            "l'interdiction de la chasse des baleines."
        ),
        "country": "Mauritanie",
        "theme": "chasse_baleines",
        "ground_truth": "Non",
        "relevant_keywords": ['période', 'baleine'],
    },

    {
        "id": "Q_BAL_099",
        "axe": 11,
        "axe_label": "Contrôle — zones",
        "question": (
            "Est-ce que en Mauritanie, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction de la chasse des baleines ? Si ces procédures existent, "
            "vérifiez si elles précisent des lieux ou zones spécifiques pour le contrôle du respect de "
            "l'interdiction de la chasse des baleines."
        ),
        "country": "Mauritanie",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Il n'y a pas d'articles spécifiques mentionnant une interdiction de chasse ou de pêche des baleines "
            "(cétacés) dans les documents fournis. Les articles 50 et 67 concernent principalement la gestion des "
            "activités de recherche océanique et halieutique, ainsi que le contrôle des pêches en Mauritanie, "
            "mais ils ne font pas référence à une interdiction spécifique de chasse ou de pêche des baleines. Il "
            "est donc difficile de répondre avec précision à votre question basée sur les informations fournies."
        ),
        "relevant_keywords": ['zone', 'baleine'],
    },

    # --- Sénégal ---

    {
        "id": "Q_BAL_100",
        "axe": 1,
        "axe_label": "Existence",
        "question": "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines au Sénégal ?",
        "country": "Sénégal",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 67(a) interdit la chasse, la capture et la commercialisation de toutes les espèces de "
            "mammifères marins au Sénégal."
        ),
        "relevant_keywords": ['interdit', 'baleine'],
    },

    {
        "id": "Q_BAL_101",
        "axe": 2,
        "axe_label": "Zonage",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines au Sénégal qui "
            "précise que cette mesure n'est applicable qu'à certaines zones, aires ou régions ?"
        ),
        "country": "Sénégal",
        "theme": "chasse_baleines",
        "ground_truth": "Non",
        "relevant_keywords": ['zone', 'mammifère'],
    },

    {
        "id": "Q_BAL_102",
        "axe": 3,
        "axe_label": "Temporalité",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines au Sénégal qui "
            "précise que cette mesure n'est pas applicable en permanence (temporalité) ?"
        ),
        "country": "Sénégal",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Il existe un article portant sur l'interdiction de la chasse, capture, détention et "
            "commercialisation de toutes les espèces de mammifères marins (Article 67(a)) dans le contexte donné. "
            "Cependant, il n'y a pas de précision concernant une éventuelle temporalité de cette interdiction au "
            "Sénégal."
        ),
        "relevant_keywords": ['période', 'mammifère'],
    },

    {
        "id": "Q_BAL_103",
        "axe": 4,
        "axe_label": "Types d\'activités concernées",
        "question": (
            "Est-ce qu'un texte juridique précise les types d'activités concernées par l'interdiction de la "
            "chasse des baleines au Sénégal ?"
        ),
        "country": "Sénégal",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 67 du Code de la Pêche maritime sénégalais interdit en tout temps et en tous lieux la "
            "pêche, la détention et la commercialisation de toutes les espèces de mammifères marins, y compris "
            "les baleines (cétacés)."
        ),
        "relevant_keywords": ['capture', 'mammifère'],
    },

    {
        "id": "Q_BAL_104",
        "axe": 5,
        "axe_label": "Exceptions hors santé/ordre/recherche",
        "question": (
            "Est-ce qu'un texte juridique mentionne des exceptions à l'interdiction de la chasse des baleines au "
            "Sénégal ? Vérifie si ce texte inclut des exceptions relatives à d'autres domaines que de la santé, "
            "de l'ordre public et de la recherche."
        ),
        "country": "Sénégal",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas d'exceptions mentionnées dans les articles fournis pour l'interdiction de la "
            "chasse, de la pêche ou de la capture des baleines (cétacés) au Sénégal."
        ),
        "relevant_keywords": [],
        "is_piege": True,
    },

    {
        "id": "Q_BAL_105",
        "axe": 6,
        "axe_label": "Exceptions / dérogations spécifiques",
        "question": (
            "Est-ce qu'un texte juridique mentionne des exceptions à l'interdiction de la chasse des baleines au "
            "Sénégal ? Ne pas inclure les délais de mise en place de la loi. Les dérogations ou autorisations "
            "spécifiques constituent des exceptions."
        ),
        "country": "Sénégal",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas d'exceptions mentionnées dans les articles juridiques fournis pour l'interdiction "
            "de la chasse, de la pêche ou de la capture des baleines (cétacés) au Sénégal."
        ),
        "relevant_keywords": ['dérogation', 'mammifère'],
    },

    {
        "id": "Q_BAL_106",
        "axe": 7,
        "axe_label": "Sanction financière",
        "question": (
            "Est-ce qu'il existe un article qui précise que l'infraction à l'interdiction de la chasse des "
            "baleines au Sénégal entraîne une sanction financière ?"
        ),
        "country": "Sénégal",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 125 précise que les infractions très graves de pêche industrielle, y compris la pêche "
            "de baleines (cétacés), sont punies d'une amende de 20.000.000 à 30.000.000 francs CFA."
        ),
        "relevant_keywords": ['amende', 'baleine'],
    },

    {
        "id": "Q_BAL_107",
        "axe": 8,
        "axe_label": "Sanction pénale",
        "question": (
            "Est-ce que l'infraction à l'interdiction de la chasse des baleines au Sénégal entraîne une peine de "
            "prison ?"
        ),
        "country": "Sénégal",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas d'article dans le contexte précisant que l'infraction à l'interdiction des "
            "baleines (cétacés) au Sénégal entraîne une peine de prison."
        ),
        "relevant_keywords": ['emprisonnement', 'baleine'],
    },

    {
        "id": "Q_BAL_108",
        "axe": 9,
        "axe_label": "Contrôle — acteurs institutionnels",
        "question": (
            "Est-ce que au Sénégal, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction de la chasse des baleines ?"
        ),
        "country": "Sénégal",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 85 stipule que les agents de surveillance peuvent inspecter les navires et leurs "
            "captures pour s'assurer du respect des règles, y compris l'interdiction de la pêche ou de la "
            "détention de mammifères marins."
        ),
        "relevant_keywords": ['administration', 'baleine'],
    },

    {
        "id": "Q_BAL_109",
        "axe": 10,
        "axe_label": "Contrôle — temporalité",
        "question": (
            "Est-ce que au Sénégal, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction de la chasse des baleines ? Si ces procédures existent, "
            "vérifiez si elles précisent des périodes (temporalité) spécifiques pour le contrôle du respect de "
            "l'interdiction de la chasse des baleines."
        ),
        "country": "Sénégal",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas de procédures de contrôle spécifiquement décrites dans les articles fournis pour "
            "garantir ou assurer le respect de l'interdiction des baleines (cétacés) au Sénégal."
        ),
        "relevant_keywords": ['période', 'baleine'],
    },

    {
        "id": "Q_BAL_110",
        "axe": 11,
        "axe_label": "Contrôle — zones",
        "question": (
            "Est-ce que au Sénégal, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction de la chasse des baleines ? Si ces procédures existent, "
            "vérifiez si elles précisent des lieux ou zones spécifiques pour le contrôle du respect de "
            "l'interdiction de la chasse des baleines."
        ),
        "country": "Sénégal",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas de procédures de contrôle spécifiquement décrites dans les articles fournis pour "
            "garantir ou assurer le respect de l'interdiction des baleines au Sénégal."
        ),
        "relevant_keywords": ['zone', 'baleine'],
    },

    # --- Togo ---

    {
        "id": "Q_BAL_111",
        "axe": 1,
        "axe_label": "Existence",
        "question": "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines au Togo ?",
        "country": "Togo",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 14 a) interdit la pêche, la détention et la commercialisation de toutes les espèces "
            "de mammifères marins protégés au Togo."
        ),
        "relevant_keywords": ['interdit', 'baleine'],
    },

    {
        "id": "Q_BAL_112",
        "axe": 2,
        "axe_label": "Zonage",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines au Togo qui "
            "précise que cette mesure n'est applicable qu'à certaines zones, aires ou régions ?"
        ),
        "country": "Togo",
        "theme": "chasse_baleines",
        "ground_truth": "non",
        "relevant_keywords": ['zone', 'mammifère'],
    },

    {
        "id": "Q_BAL_113",
        "axe": 3,
        "axe_label": "Temporalité",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines au Togo qui "
            "précise que cette mesure n'est pas applicable en permanence (temporalité) ?"
        ),
        "country": "Togo",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas d'article dans ce contexte qui détaillerait l'interdiction de la chasse, pêche ou "
            "capture de baleines (cétacés) au Togo et mentionnant que cette interdiction n'est pas applicable en "
            "permanence."
        ),
        "relevant_keywords": ['période', 'mammifère'],
    },

    {
        "id": "Q_BAL_114",
        "axe": 4,
        "axe_label": "Types d\'activités concernées",
        "question": (
            "Est-ce qu'un texte juridique précise les types d'activités concernées par l'interdiction de la "
            "chasse des baleines au Togo ?"
        ),
        "country": "Togo",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 14 du document \"ARRETE N°68-10/MAEP/Cab/SG/DPA fixant les modalités d'exploitation "
            "des ressources halieutiques dans les eaux marines sous juridiction togolaise\" précise que la pêche, "
            "la détention et la commercialisation de toutes les espèces de mammifères marins protégés sont "
            "interdites en tous temps et en tous lieux au Togo."
        ),
        "relevant_keywords": ['capture', 'mammifère'],
    },

    {
        "id": "Q_BAL_115",
        "axe": 5,
        "axe_label": "Exceptions hors santé/ordre/recherche",
        "question": (
            "Est-ce qu'un texte juridique mentionne des exceptions à l'interdiction de la chasse des baleines au "
            "Togo ? Vérifie si ce texte inclut des exceptions relatives à d'autres domaines que de la santé, de "
            "l'ordre public et de la recherche."
        ),
        "country": "Togo",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas d'exceptions mentionnées dans l'article juridique fourni pour l'interdiction de la "
            "chasse, de la pêche ou de la capture des baleines (cétacés) au Togo."
        ),
        "relevant_keywords": [],
        "is_piege": True,
    },

    {
        "id": "Q_BAL_116",
        "axe": 6,
        "axe_label": "Exceptions / dérogations spécifiques",
        "question": (
            "Est-ce qu'un texte juridique mentionne des exceptions à l'interdiction de la chasse des baleines au "
            "Togo ? Ne pas inclure les délais de mise en place de la loi. Les dérogations ou autorisations "
            "spécifiques constituent des exceptions."
        ),
        "country": "Togo",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas d'exceptions mentionnées dans les articles fournis pour l'interdiction de la "
            "chasse, de la pêche ou de la capture des baleines (cétacés) au Togo."
        ),
        "relevant_keywords": ['dérogation', 'mammifère'],
    },

    {
        "id": "Q_BAL_117",
        "axe": 7,
        "axe_label": "Sanction financière",
        "question": (
            "Est-ce qu'il existe un article qui précise que l'infraction à l'interdiction de la chasse des "
            "baleines au Togo entraîne une sanction financière ?"
        ),
        "country": "Togo",
        "theme": "chasse_baleines",
        "ground_truth": "Non",
        "relevant_keywords": ['amende', 'baleine'],
    },

    {
        "id": "Q_BAL_118",
        "axe": 8,
        "axe_label": "Sanction pénale",
        "question": (
            "Est-ce que l'infraction à l'interdiction de la chasse des baleines au Togo entraîne une peine de "
            "prison ?"
        ),
        "country": "Togo",
        "theme": "chasse_baleines",
        "ground_truth": "Non",
        "relevant_keywords": ['emprisonnement', 'baleine'],
    },

    {
        "id": "Q_BAL_119",
        "axe": 9,
        "axe_label": "Contrôle — acteurs institutionnels",
        "question": (
            "Est-ce que au Togo, des procédures de contrôle sont spécifiquement décrites pour garantir ou assurer "
            "le respect de l'interdiction de la chasse des baleines ?"
        ),
        "country": "Togo",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 12 spécifie que les navires ou pirogues autorisés à pêcher dans les eaux sous "
            "juridiction togolaise sont soumis à une inspection des pêches avant le débarquement de leur "
            "cargaison. Cela inclut probablement la vérification de l'interdiction de chasse, pêche ou capture de "
            "baleines (cétacés)."
        ),
        "relevant_keywords": ['administration', 'baleine'],
    },

    {
        "id": "Q_BAL_120",
        "axe": 10,
        "axe_label": "Contrôle — temporalité",
        "question": (
            "Est-ce que au Togo, des procédures de contrôle sont spécifiquement décrites pour garantir ou assurer "
            "le respect de l'interdiction de la chasse des baleines ? Si ces procédures existent, vérifiez si "
            "elles précisent des périodes (temporalité) spécifiques pour le contrôle du respect de l'interdiction "
            "de la chasse des baleines."
        ),
        "country": "Togo",
        "theme": "chasse_baleines",
        "ground_truth": "Période prévue à l'article 12: \"avant le débarquement de leur cargaison\"",
        "relevant_keywords": ['période', 'baleine'],
    },

    {
        "id": "Q_BAL_121",
        "axe": 11,
        "axe_label": "Contrôle — zones",
        "question": (
            "Est-ce que au Togo, des procédures de contrôle sont spécifiquement décrites pour garantir ou assurer "
            "le respect de l'interdiction de la chasse des baleines ? Si ces procédures existent, vérifiez si "
            "elles précisent des lieux ou zones spécifiques pour le contrôle du respect de l'interdiction de la "
            "chasse des baleines."
        ),
        "country": "Togo",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 14 interdit la pêche, la détention et la commercialisation de toutes les espèces de "
            "mammifères marins protégés au Togo. L'article 12 décrit des procédures de contrôle pour garantir le "
            "respect de cette interdiction, en prévoyant une inspection des pêches avant le débarquement de la "
            "cargaison des navires autorisés à pêcher dans les eaux sous juridiction togolaise."
        ),
        "relevant_keywords": ['zone', 'baleine'],
    },

    # --- Tunisie ---

    {
        "id": "Q_BAL_122",
        "axe": 1,
        "axe_label": "Existence",
        "question": "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines en Tunisie ?",
        "country": "Tunisie",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Oui, l'article 18 interdit la pêche aux baleines et autres espèces aquatiques à l'exception des "
            "grands et petits pélagiques en Tunisie."
        ),
        "relevant_keywords": ['interdit', 'baleine'],
    },

    {
        "id": "Q_BAL_123",
        "axe": 2,
        "axe_label": "Zonage",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines en Tunisie qui "
            "précise que cette mesure n'est applicable qu'à certaines zones, aires ou régions ?"
        ),
        "country": "Tunisie",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas d'article portant sur l'interdiction de la chasse, pêche ou capture des baleines "
            "(cétacés) qui précise que cette mesure est applicable uniquement à certaines zones, aires ou régions "
            "en Tunisie dans les documents fournis."
        ),
        "relevant_keywords": ['zone', 'mammifère'],
    },

    {
        "id": "Q_BAL_124",
        "axe": 3,
        "axe_label": "Temporalité",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines en Tunisie qui "
            "précise que cette mesure n'est pas applicable en permanence (temporalité) ?"
        ),
        "country": "Tunisie",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas d'article portant sur l'interdiction des baleines (cétacés) avec une précision sur "
            "la temporalité en Tunisie dans ce contexte."
        ),
        "relevant_keywords": ['période', 'mammifère'],
    },

    {
        "id": "Q_BAL_125",
        "axe": 4,
        "axe_label": "Types d\'activités concernées",
        "question": (
            "Est-ce qu'un texte juridique précise les types d'activités concernées par l'interdiction de la "
            "chasse des baleines en Tunisie ?"
        ),
        "country": "Tunisie",
        "theme": "chasse_baleines",
        "ground_truth": "Il n'y a pas de contexte juridique disponible.",
        "relevant_keywords": ['capture', 'mammifère'],
    },

    {
        "id": "Q_BAL_126",
        "axe": 5,
        "axe_label": "Exceptions hors santé/ordre/recherche",
        "question": (
            "Est-ce qu'un texte juridique mentionne des exceptions à l'interdiction de la chasse des baleines en "
            "Tunisie ? Vérifie si ce texte inclut des exceptions relatives à d'autres domaines que de la santé, "
            "de l'ordre public et de la recherche."
        ),
        "country": "Tunisie",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas d'exceptions mentionnées dans l'article juridique fourni concernant l'interdiction "
            "de la pêche des baleines (cétacés) en Tunisie."
        ),
        "relevant_keywords": [],
        "is_piege": True,
    },

    {
        "id": "Q_BAL_127",
        "axe": 6,
        "axe_label": "Exceptions / dérogations spécifiques",
        "question": (
            "Est-ce qu'un texte juridique mentionne des exceptions à l'interdiction de la chasse des baleines en "
            "Tunisie ? Ne pas inclure les délais de mise en place de la loi. Les dérogations ou autorisations "
            "spécifiques constituent des exceptions."
        ),
        "country": "Tunisie",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, il n'y a pas d'exceptions mentionnées pour la chasse, la pêche ou la capture des baleines "
            "(cétacés) dans l'article juridique fourni."
        ),
        "relevant_keywords": ['dérogation', 'mammifère'],
    },

    {
        "id": "Q_BAL_128",
        "axe": 7,
        "axe_label": "Sanction financière",
        "question": (
            "Est-ce qu'il existe un article qui précise que l'infraction à l'interdiction de la chasse des "
            "baleines en Tunisie entraîne une sanction financière ?"
        ),
        "country": "Tunisie",
        "theme": "chasse_baleines",
        "ground_truth": "Non",
        "relevant_keywords": ['amende', 'baleine'],
    },

    {
        "id": "Q_BAL_129",
        "axe": 8,
        "axe_label": "Sanction pénale",
        "question": (
            "Est-ce que l'infraction à l'interdiction de la chasse des baleines en Tunisie entraîne une peine de "
            "prison ?"
        ),
        "country": "Tunisie",
        "theme": "chasse_baleines",
        "ground_truth": (
            "D'après les informations fournies, il n'y a pas d'articles juridiques pour répondre à la question "
            "concernant la chasse, la pêche ou la capture de baleines (cétacés) en Tunisie. Il est donc "
            "impossible de fournir une réponse basée uniquement sur ces informations."
        ),
        "relevant_keywords": ['emprisonnement', 'baleine'],
    },

    {
        "id": "Q_BAL_130",
        "axe": 9,
        "axe_label": "Contrôle — acteurs institutionnels",
        "question": (
            "Est-ce que en Tunisie, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction de la chasse des baleines ?"
        ),
        "country": "Tunisie",
        "theme": "chasse_baleines",
        "ground_truth": (
            "D'après l'article 43 de l'arrêté tunisien réglementant la pêche, il est mentionné qu'une commission "
            "consultative composée de représentants de différents ministères est créée pour octroyer des "
            "autorisations de pêche après enquête administrative et avis de cette commission. Cependant, il n'est "
            "pas spécifique à la surveillance ou au contrôle du respect de l'interdiction de la chasse ou de "
            "l'exploitation des baleines (cétacés). Il n'y a pas d'informations sur les instances administratives "
            "chargées spécifiquement de superviser l'application de cette interdiction dans ce contexte."
        ),
        "relevant_keywords": ['administration', 'baleine'],
    },

    {
        "id": "Q_BAL_131",
        "axe": 10,
        "axe_label": "Contrôle — temporalité",
        "question": (
            "Est-ce que en Tunisie, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction de la chasse des baleines ? Si ces procédures existent, "
            "vérifiez si elles précisent des périodes (temporalité) spécifiques pour le contrôle du respect de "
            "l'interdiction de la chasse des baleines."
        ),
        "country": "Tunisie",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Non, les documents fournis ne contiennent pas de procédures spécifiques de contrôle pour garantir ou "
            "assurer le respect de l'interdiction des baleines (cétacés) en Tunisie."
        ),
        "relevant_keywords": ['période', 'baleine'],
    },

    {
        "id": "Q_BAL_132",
        "axe": 11,
        "axe_label": "Contrôle — zones",
        "question": (
            "Est-ce que en Tunisie, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction de la chasse des baleines ? Si ces procédures existent, "
            "vérifiez si elles précisent des lieux ou zones spécifiques pour le contrôle du respect de "
            "l'interdiction de la chasse des baleines."
        ),
        "country": "Tunisie",
        "theme": "chasse_baleines",
        "ground_truth": (
            "Il n'y a pas de mention explicite de procédures de contrôle spécifiques pour garantir ou assurer le "
            "respect de l'interdiction des baleines (cétacés) dans les articles fournis. Il est donc impossible "
            "de répondre affirmativement à cette question basée uniquement sur ces informations."
        ),
        "relevant_keywords": ['zone', 'baleine'],
    },


    # =========================================================================
    # THÈME 2 — REJETS D'HYDROCARBURES
    # Pays : Bénin, Cameroun, Comores, Congo, Côte d'Ivoire, Djibouti, Gabon, Guinée, Maroc, Mauritanie, Sénégal, Togo
    # =========================================================================

    # --- Bénin ---

    {
        "id": "Q_HYD_001",
        "axe": 1,
        "axe_label": "Existence",
        "question": "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures au Bénin ?",
        "country": "Bénin",
        "theme": "rejets_hydrocarbures",
        "ground_truth": "Oui, il existe un article portant sur l'interdiction du rejet d'hydrocarbures au Bénin : Article 68.",
        "relevant_keywords": ['interdit', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_002",
        "axe": 2,
        "axe_label": "Zonage",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures au Bénin qui "
            "précise que cette mesure n'est applicable qu'à certaines zones, aires ou régions ?"
        ),
        "country": "Bénin",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Non, il n'y a pas d'article portant sur l'interdiction du rejet d'hydrocarbures qui précise que "
            "cette mesure n'est applicable qu'à certaines zones, aires ou régions au Bénin dans les documents "
            "fournis."
        ),
        "relevant_keywords": ['zone', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_003",
        "axe": 3,
        "axe_label": "Temporalité",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures au Bénin qui "
            "précise que cette mesure n'est pas applicable en permanence (temporalité) ?"
        ),
        "country": "Bénin",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Non, il n'y a pas d'article portant sur l'interdiction du rejet d'hydrocarbures qui précise une "
            "exception temporelle au Bénin dans le contexte fourni."
        ),
        "relevant_keywords": ['période', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_004",
        "axe": 4,
        "axe_label": "Types d\'activités concernées",
        "question": (
            "Est-ce que le texte juridique précise les types d'activités concernées par l'interdiction du rejet "
            "d'hydrocarbures au Bénin ?"
        ),
        "country": "Bénin",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, le texte juridique précise que l'interdiction de rejeter des hydrocarbures s'applique aux "
            "navires traversant ou séjournant dans les zones maritimes sous souveraineté ou juridiction béninoise "
            "(Article 55)."
        ),
        "relevant_keywords": ['navire', 'rejet'],
    },

    {
        "id": "Q_HYD_005",
        "axe": 5,
        "axe_label": "Exceptions hors santé/ordre/recherche",
        "question": (
            "Est-ce que le texte juridique mentionne des exceptions à l'interdiction du rejet d'hydrocarbures au "
            "Bénin ? Vérifie si ce texte inclut des exceptions relatives à d'autres domaines que de la santé, de "
            "l'ordre public et de la recherche."
        ),
        "country": "Bénin",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, il y a des exceptions mentionnées dans l'article 68 qui permettent le rejet d'hydrocarbures si "
            "toutes les conditions prévues par les conventions internationales sont réunies."
        ),
        "relevant_keywords": [],
        "is_piege": True,
    },

    {
        "id": "Q_HYD_006",
        "axe": 6,
        "axe_label": "Exceptions / dérogations spécifiques",
        "question": (
            "Est-ce que le texte juridique mentionne des exceptions à l'interdiction du rejet d'hydrocarbures au "
            "Bénin ?"
        ),
        "country": "Bénin",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, l'article 68 mentionne une exception à l'interdiction du rejet d'hydrocarbures dans les zones "
            "maritimes béninoises : \"toutes les conditions prévues par les conventions internationales\"."
        ),
        "relevant_keywords": ['dérogation', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_007",
        "axe": 7,
        "axe_label": "Sanction financière",
        "question": "Est-ce que le rejet d'hydrocarbures au Bénin entraîne une sanction financière (amende) ?",
        "country": "Bénin",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, selon l'article 68 du code maritime béninois, il est interdit de rejeter des hydrocarbures ou "
            "des mélanges d'hydrocarbures dans les zones maritimes béninoises, sous peine d'une amende."
        ),
        "relevant_keywords": ['amende', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_008",
        "axe": 8,
        "axe_label": "Sanction pénale",
        "question": "Est-ce que le rejet d'hydrocarbures au Bénin entraîne une peine de prison ?",
        "country": "Bénin",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, selon l'article 638 de la loi n°2010-11 du 7 mars 2011 portant code maritime en République du "
            "Bénin, le rejet d'hydrocarbures dans les eaux territoriales béninoises peut entraîner une peine "
            "d'emprisonnement allant de un (01) à cinq (05) ans."
        ),
        "relevant_keywords": ['emprisonnement', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_009",
        "axe": 9,
        "axe_label": "Contrôle — acteurs institutionnels",
        "question": (
            "Est-ce que au Bénin, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction du rejet d'hydrocarbures ?"
        ),
        "country": "Bénin",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Non, il n'y a pas de procédures spécifiques mentionnées dans les articles fournis pour garantir le "
            "respect de l'interdiction du rejet d'hydrocarbures au Bénin."
        ),
        "relevant_keywords": ['administration', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_010",
        "axe": 10,
        "axe_label": "Contrôle — temporalité",
        "question": (
            "Est-ce que au Bénin, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction du rejet d'hydrocarbures ? Si ces procédures existent, vérifiez "
            "si elles précisent des périodes (temporalité) spécifiques pour le contrôle du respect de "
            "l'interdiction du rejet d'hydrocarbures."
        ),
        "country": "Bénin",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Non, il n'y a pas de procédures de contrôle spécifiquement décrites dans les articles fournis pour "
            "garantir ou assurer le respect de l'interdiction du rejet d'hydrocarbures au Bénin."
        ),
        "relevant_keywords": ['période', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_011",
        "axe": 11,
        "axe_label": "Contrôle — zones",
        "question": (
            "Est-ce que au Bénin, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction du rejet d'hydrocarbures ? Si ces procédures existent, vérifiez "
            "si elles précisent des lieux ou zones spécifiques pour le contrôle du respect de l'interdiction du "
            "rejet d'hydrocarbures."
        ),
        "country": "Bénin",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Non, il n'y a pas de procédures de contrôle spécifiquement décrites dans les articles fournis pour "
            "garantir ou assurer le respect de l'interdiction du rejet d'hydrocarbures au Bénin."
        ),
        "relevant_keywords": ['zone', 'hydrocarbure'],
    },

    # --- Cameroun ---

    {
        "id": "Q_HYD_012",
        "axe": 1,
        "axe_label": "Existence",
        "question": "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures au Cameroun ?",
        "country": "Cameroun",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, l'article 83 porte sur l'interdiction du rejet d'hydrocarbures dans les eaux maritimes sous "
            "juridiction camerounaise et prévoit des peines pour les contrevenants."
        ),
        "relevant_keywords": ['interdit', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_013",
        "axe": 2,
        "axe_label": "Zonage",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures au Cameroun qui "
            "précise que cette mesure n'est applicable qu'à certaines zones, aires ou régions ?"
        ),
        "country": "Cameroun",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Il n'y a pas d'article juridique spécifique portant sur une interdiction ciblée du rejet "
            "d'hydrocarbures dans certaines zones, aires ou régions spécifiques au Cameroun dans le contexte "
            "fourni."
        ),
        "relevant_keywords": ['zone', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_014",
        "axe": 3,
        "axe_label": "Temporalité",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures au Cameroun qui "
            "précise que cette mesure n'est pas applicable en permanence (temporalité) ?"
        ),
        "country": "Cameroun",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Non, il n'y a pas d'article juridique dans le contexte fournie qui porte sur une interdiction du "
            "rejet d'hydrocarbures avec une exception temporelle au Cameroun."
        ),
        "relevant_keywords": ['période', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_015",
        "axe": 4,
        "axe_label": "Types d\'activités concernées",
        "question": (
            "Est-ce que le texte juridique précise les types d'activités concernées par l'interdiction du rejet "
            "d'hydrocarbures au Cameroun ?"
        ),
        "country": "Cameroun",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, l'article 83(1) spécifie que l'interdiction s'applique aux capitaines de navires qui rejettent "
            "des hydrocarbures ou d'autres substances liquides nocives pour le milieu marin dans les eaux "
            "maritimes sous juridiction camerounaise."
        ),
        "relevant_keywords": ['navire', 'rejet'],
    },

    {
        "id": "Q_HYD_016",
        "axe": 5,
        "axe_label": "Exceptions hors santé/ordre/recherche",
        "question": (
            "Est-ce que le texte juridique mentionne des exceptions à l'interdiction du rejet d'hydrocarbures au "
            "Cameroun ? Vérifie si ce texte inclut des exceptions relatives à d'autres domaines que de la santé, "
            "de l'ordre public et de la recherche."
        ),
        "country": "Cameroun",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, il y a une exception mentionnée dans l'article 83(4) qui stipule que les pénalités prévues ne "
            "s'appliquent pas aux rejets effectués par un navire pour assurer sa propre sécurité ou celle "
            "d’autres navires, ou pour sauver des vies humaines, ni aux déversements résultant de dommages subis "
            "par le navire sans qu'une faute ne puisse être établie à l'encontre de son capitaine ou de son "
            "équipage."
        ),
        "relevant_keywords": [],
        "is_piege": True,
    },

    {
        "id": "Q_HYD_017",
        "axe": 6,
        "axe_label": "Exceptions / dérogations spécifiques",
        "question": (
            "Est-ce que le texte juridique mentionne des exceptions à l'interdiction du rejet d'hydrocarbures au "
            "Cameroun ?"
        ),
        "country": "Cameroun",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, il y a une exception mentionnée dans l'article 83(4) qui stipule que les pénalités prévues ne "
            "s'appliquent pas aux rejets effectués par un navire pour assurer sa propre sécurité ou celle "
            "d’autres navires, ou pour sauver des vies humaines, ni aux déversements résultant de dommages subis "
            "par le navire sans qu'une faute ne puisse être établie à l'encontre de son capitaine ou de son "
            "équipage."
        ),
        "relevant_keywords": ['dérogation', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_018",
        "axe": 7,
        "axe_label": "Sanction financière",
        "question": "Est-ce que le rejet d'hydrocarbures au Cameroun entraîne une sanction financière (amende) ?",
        "country": "Cameroun",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, selon l'article 83 de la loi camerounaise n°96-12 portant loi-cadre relative à la gestion de "
            "l'environnement, le rejet d'hydrocarbures dans les eaux maritimes sous juridiction camerounaise "
            "entraîne une amende de dix millions (10.000.000) à cinquante millions (50.000.000) de FCFA."
        ),
        "relevant_keywords": ['amende', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_019",
        "axe": 8,
        "axe_label": "Sanction pénale",
        "question": "Est-ce que le rejet d'hydrocarbures au Cameroun entraîne une peine de prison ?",
        "country": "Cameroun",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, selon l'article 83 de la loi camerounaise n°96-12 portant loi-cadre relative à la gestion de "
            "l'environnement, le rejet d'hydrocarbures dans les eaux maritimes sous juridiction camerounaise peut "
            "entraîner une peine d'emprisonnement allant de six mois à un an."
        ),
        "relevant_keywords": ['emprisonnement', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_020",
        "axe": 9,
        "axe_label": "Contrôle — acteurs institutionnels",
        "question": (
            "Est-ce que au Cameroun, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction du rejet d'hydrocarbures ?"
        ),
        "country": "Cameroun",
        "theme": "rejets_hydrocarbures",
        "ground_truth": "Oui",
        "relevant_keywords": ['administration', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_021",
        "axe": 10,
        "axe_label": "Contrôle — temporalité",
        "question": (
            "Est-ce que au Cameroun, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction du rejet d'hydrocarbures ? Si ces procédures existent, vérifiez "
            "si elles précisent des périodes (temporalité) spécifiques pour le contrôle du respect de "
            "l'interdiction du rejet d'hydrocarbures."
        ),
        "country": "Cameroun",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Non, il n'y a pas de procédures de contrôle spécifiquement décrites dans les articles fournis pour "
            "garantir ou assurer le respect de l'interdiction du rejet d'hydrocarbures au Cameroun."
        ),
        "relevant_keywords": ['période', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_022",
        "axe": 11,
        "axe_label": "Contrôle — zones",
        "question": (
            "Est-ce que au Cameroun, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction du rejet d'hydrocarbures ? Si ces procédures existent, vérifiez "
            "si elles précisent des lieux ou zones spécifiques pour le contrôle du respect de l'interdiction du "
            "rejet d'hydrocarbures."
        ),
        "country": "Cameroun",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Je suis désolé, il n'y a pas suffisamment de détails dans les articles juridiques fournis pour "
            "répondre à votre question spécifique concernant des procédures de contrôle spécifiques pour garantir "
            "ou assurer le respect de l'interdiction du rejet d'hydrocarbures au Cameroun. Les articles ne font "
            "pas référence à une administration, un comité, un service ou un agent pour superviser, évaluer ou "
            "constater l'application de cette interdiction, ni ne précisent des lieux ou zones spécifiques pour "
            "le contrôle du respect de l'interdiction du rejet d'hydrocarbures."
        ),
        "relevant_keywords": ['zone', 'hydrocarbure'],
    },

    # --- Comores ---

    {
        "id": "Q_HYD_023",
        "axe": 1,
        "axe_label": "Existence",
        "question": "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures aux Comores ?",
        "country": "Comores",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, il existe deux articles portant sur l'interdiction du rejet d'hydrocarbures aux Comores : "
            "l'article 424 et l'article 425."
        ),
        "relevant_keywords": ['interdit', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_024",
        "axe": 2,
        "axe_label": "Zonage",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures aux Comores qui "
            "précise que cette mesure n'est applicable qu'à certaines zones, aires ou régions ?"
        ),
        "country": "Comores",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, l'article 424 spécifie que l'interdiction de rejet d'hydrocarbures s'applique uniquement dans "
            "les eaux maritimes comoriennes et non dans la zone économique exclusive."
        ),
        "relevant_keywords": ['zone', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_025",
        "axe": 3,
        "axe_label": "Temporalité",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures aux Comores qui "
            "précise que cette mesure n'est pas applicable en permanence (temporalité) ?"
        ),
        "country": "Comores",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, l'article 424 prévoit des conditions dans lesquelles le rejet d'hydrocarbures est autorisé, "
            "indiquant ainsi une temporalité limitée pour cette interdiction."
        ),
        "relevant_keywords": ['période', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_026",
        "axe": 4,
        "axe_label": "Types d\'activités concernées",
        "question": (
            "Est-ce que le texte juridique précise les types d'activités concernées par l'interdiction du rejet "
            "d'hydrocarbures aux Comores ?"
        ),
        "country": "Comores",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, le texte juridique précise les types d'activités concernées par l'interdiction du rejet "
            "d'hydrocarbures aux Comores. Selon l'article 424, l'interdiction s'applique à tous les navires "
            "autres que les pétroliers, tandis que selon l'article 425, elle s'applique spécifiquement aux "
            "pétroliers."
        ),
        "relevant_keywords": ['navire', 'rejet'],
    },

    {
        "id": "Q_HYD_027",
        "axe": 5,
        "axe_label": "Exceptions hors santé/ordre/recherche",
        "question": (
            "Est-ce que le texte juridique mentionne des exceptions à l'interdiction du rejet d'hydrocarbures aux "
            "Comores ? Vérifie si ce texte inclut des exceptions relatives à d'autres domaines que de la santé, "
            "de l'ordre public et de la recherche."
        ),
        "country": "Comores",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, il y a des exceptions à l'interdiction du rejet d'hydrocarbures aux Comores. Selon l'article "
            "424, les navires autres que les pétroliers peuvent rejeter des hydrocarbures dans certaines "
            "conditions, notamment lorsqu'ils sont en route et hors des eaux territoriales. L'article 425 prévoit "
            "également des exceptions pour les pétroliers, sous réserve de certaines conditions telles que la "
            "distance par rapport aux lignes de base servant à déterminer la mer territoriale et le taux "
            "instantané du rejet d'hydrocarbures."
        ),
        "relevant_keywords": [],
        "is_piege": True,
    },

    {
        "id": "Q_HYD_028",
        "axe": 6,
        "axe_label": "Exceptions / dérogations spécifiques",
        "question": (
            "Est-ce que le texte juridique mentionne des exceptions à l'interdiction du rejet d'hydrocarbures aux "
            "Comores ?"
        ),
        "country": "Comores",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, il y a des exceptions à l'interdiction du rejet d'hydrocarbures aux Comores. Selon l'article "
            "424, les navires autres que les pétroliers peuvent rejeter des hydrocarbures dans certaines "
            "conditions, notamment lorsqu'ils sont en route et hors des eaux territoriales. L'article 425 prévoit "
            "également des exceptions pour les pétroliers, sous réserve de certaines conditions telles que la "
            "distance par rapport aux lignes de base servant à déterminer la mer territoriale et le taux "
            "instantané du rejet d'hydrocarbures."
        ),
        "relevant_keywords": ['dérogation', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_029",
        "axe": 7,
        "axe_label": "Sanction financière",
        "question": "Est-ce que le rejet d'hydrocarbures aux Comores entraîne une sanction financière (amende) ?",
        "country": "Comores",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, selon l'article 401 du Code de la Marine Marchande Comorienne, le rejet direct ou indirect "
            "d'hydrocarbures en mer est passible d'une amende allant de 1.000.000 KMF à 10.000.000 KMF de francs "
            "comoriens"
        ),
        "relevant_keywords": ['amende', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_030",
        "axe": 8,
        "axe_label": "Sanction pénale",
        "question": "Est-ce que le rejet d'hydrocarbures aux Comores entraîne une peine de prison ?",
        "country": "Comores",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, selon l'article 463 du Code de la Marine Marchande Comorienne, le rejet d'hydrocarbures peut "
            "entraîner une peine d'emprisonnement allant de six mois à trois ans."
        ),
        "relevant_keywords": ['emprisonnement', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_031",
        "axe": 9,
        "axe_label": "Contrôle — acteurs institutionnels",
        "question": (
            "Est-ce que aux Comores, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction du rejet d'hydrocarbures ?"
        ),
        "country": "Comores",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Il existe des procédures de contrôle spécifiques aux Comores pour garantir le respect de "
            "l'interdiction du rejet d'hydrocarbures"
        ),
        "relevant_keywords": ['administration', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_032",
        "axe": 10,
        "axe_label": "Contrôle — temporalité",
        "question": (
            "Est-ce que aux Comores, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction du rejet d'hydrocarbures ? Si ces procédures existent, vérifiez "
            "si elles précisent des périodes (temporalité) spécifiques pour le contrôle du respect de "
            "l'interdiction du rejet d'hydrocarbures."
        ),
        "country": "Comores",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Il existe des procédures de contrôle spécifiques aux Comores pour garantir le respect de "
            "l'interdiction du rejet d'hydrocarbures, prévues dans la Convention OPRC/HNS. L' instance chargée de "
            "superviser et constater l'application de cette interdiction est l'Union des Comores. Les périodes "
            "spécifiques prévues pour le contrôle du respect de cette interdiction ne sont pas spécifiées dans "
            "les articles fournis"
        ),
        "relevant_keywords": ['période', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_033",
        "axe": 11,
        "axe_label": "Contrôle — zones",
        "question": (
            "Est-ce que aux Comores, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction du rejet d'hydrocarbures ? Si ces procédures existent, vérifiez "
            "si elles précisent des lieux ou zones spécifiques pour le contrôle du respect de l'interdiction du "
            "rejet d'hydrocarbures."
        ),
        "country": "Comores",
        "theme": "rejets_hydrocarbures",
        "ground_truth": "Non",
        "relevant_keywords": ['zone', 'hydrocarbure'],
    },

    # --- Congo ---

    {
        "id": "Q_HYD_034",
        "axe": 1,
        "axe_label": "Existence",
        "question": "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures au Congo ?",
        "country": "Congo",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, il existe un article portant sur l'interdiction du rejet d'hydrocarbures au Congo. Article 29 : "
            "\"Sont interdits le déversement, l'immersion et l'incinération dans les eaux marines et "
            "continentales sous juridiction congolaise, de substances de toute nature susceptible de...\""
        ),
        "relevant_keywords": ['interdit', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_035",
        "axe": 2,
        "axe_label": "Zonage",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures au Congo qui "
            "précise que cette mesure n'est applicable qu'à certaines zones, aires ou régions ?"
        ),
        "country": "Congo",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Non, il n'y a pas d'article portant sur l'interdiction du rejet d'hydrocarbures qui précise que "
            "cette mesure n'est applicable qu'à certaines zones, aires ou régions au Congo dans les documents "
            "fournis."
        ),
        "relevant_keywords": ['zone', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_036",
        "axe": 3,
        "axe_label": "Temporalité",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures au Congo qui "
            "précise que cette mesure n'est pas applicable en permanence (temporalité) ?"
        ),
        "country": "Congo",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, l'article 29 de la loi n°33-2023 portant gestion durable de l'environnement en République du "
            "Congo stipule que le rejet d'hydrocarbures est interdit, mais cette interdiction ne s'applique pas "
            "en permanence. L'article précise que les dispositions ne s'appliquent pas au rejet d'hydrocarbures "
            "effectué par un navire pour assurer sa propre sécurité ou celle d'un autre navire, pour éviter une "
            "avarie à la cargaison, ou sauver des vies humaines en danger. Cependant, ce rejet est soumis à "
            "autorisation préalable de l'Autorité Maritime ou fluviale et le propriétaire du navire a "
            "l'obligation de réparer les dommages causés à l'Environnement et d'en payer les dommages et "
            "intérêts."
        ),
        "relevant_keywords": ['période', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_037",
        "axe": 4,
        "axe_label": "Types d\'activités concernées",
        "question": (
            "Est-ce que le texte juridique précise les types d'activités concernées par l'interdiction du rejet "
            "d'hydrocarbures au Congo ?"
        ),
        "country": "Congo",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Non, le texte juridique ne précise pas explicitement les types d'activités concernées par "
            "l'interdiction du rejet d'hydrocarbures au Congo."
        ),
        "relevant_keywords": ['navire', 'rejet'],
    },

    {
        "id": "Q_HYD_038",
        "axe": 5,
        "axe_label": "Exceptions hors santé/ordre/recherche",
        "question": (
            "Est-ce que le texte juridique mentionne des exceptions à l'interdiction du rejet d'hydrocarbures au "
            "Congo ? Vérifie si ce texte inclut des exceptions relatives à d'autres domaines que de la santé, de "
            "l'ordre public et de la recherche."
        ),
        "country": "Congo",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, il y a une exception mentionnée dans l'article 29 de la loi n° 33 - 2023 du 17 novembre 2023 "
            "portant gestion durable de l'environnement en République du Congo. Cette exception concerne le rejet "
            "d'hydrocarbures effectué par un navire pour assurer sa propre sécurité ou celle d'un autre navire, "
            "pour éviter une avarie à la cargaison, ou sauver des vies humaines en danger. Cependant, cette "
            "exception est soumise à autorisation préalable de l'Autorité Maritime ou fluviale et le propriétaire "
            "du navire a l'obligation de réparer les dommages causés à l'Environnement et est également tenu d'en "
            "payer les dommages et intérêts."
        ),
        "relevant_keywords": [],
        "is_piege": True,
    },

    {
        "id": "Q_HYD_039",
        "axe": 6,
        "axe_label": "Exceptions / dérogations spécifiques",
        "question": (
            "Est-ce que le texte juridique mentionne des exceptions à l'interdiction du rejet d'hydrocarbures au "
            "Congo ?"
        ),
        "country": "Congo",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, il y a une exception mentionnée dans l'article 35 de la loi n° 33 - 2023 du 17 novembre 2023 "
            "portant gestion durable de l'environnement en République du Congo. Cette exception concerne le rejet "
            "d'hydrocarbures ou de mélange d'hydrocarbures effectué par un navire pour assurer sa propre sécurité "
            "où celle d'un autre navire, pour éviter une avarie à la cargaison ou sauver des vies humaines en "
            "danger. Cependant, cette exception est soumise à autorisation préalable des autorités chargées des "
            "affaires maritimes, fluviales, des hydrocarbures et de l'administration en charge de "
            "l'environnement."
        ),
        "relevant_keywords": ['dérogation', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_040",
        "axe": 7,
        "axe_label": "Sanction financière",
        "question": "Est-ce que le rejet d'hydrocarbures au Congo entraîne une sanction financière (amende) ?",
        "country": "Congo",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, selon l'article 146 de la loi n°33-2023 du Congo portant gestion durable de l'environnement, le "
            "rejet d'hydrocarbures dans les eaux maritimes ou continentales entraîne une amende comprise entre 50 "
            "000 000 et 1 000 000 000 de francs CFA."
        ),
        "relevant_keywords": ['amende', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_041",
        "axe": 8,
        "axe_label": "Sanction pénale",
        "question": "Est-ce que le rejet d'hydrocarbures au Congo entraîne une peine de prison ?",
        "country": "Congo",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, selon l'article 146 de la loi n°33-2023 du 17 novembre 2023 portant gestion durable de "
            "l'environnement en République du Congo, le rejet d'hydrocarbures dans les eaux maritimes ou "
            "continentales est puni d'un emprisonnement d'un à deux ans."
        ),
        "relevant_keywords": ['emprisonnement', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_042",
        "axe": 9,
        "axe_label": "Contrôle — acteurs institutionnels",
        "question": (
            "Est-ce que au Congo, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction du rejet d'hydrocarbures ?"
        ),
        "country": "Congo",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, les procédures de contrôle sont spécifiquement décrites dans l'article 121 de la loi n°33-2023 "
            "portant gestion durable de l'environnement en République du Congo. Cette loi prévoit que les "
            "infractions sont constatées sur la base d'un contrôle sur pièces ou sur les lieux, et qu'une "
            "notification est adressée à la personne contrôlée."
        ),
        "relevant_keywords": ['administration', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_043",
        "axe": 10,
        "axe_label": "Contrôle — temporalité",
        "question": (
            "Est-ce que au Congo, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction du rejet d'hydrocarbures ? Si ces procédures existent, vérifiez "
            "si elles précisent des périodes (temporalité) spécifiques pour le contrôle du respect de "
            "l'interdiction du rejet d'hydrocarbures."
        ),
        "country": "Congo",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, les articles 34 et 29 spécifient que les rejets d'hydrocarbures sont interdits, mais ils "
            "prévoient des exceptions pour assurer la sécurité des navires. Les articles 24 et 121 précisent que "
            "l'administration compétente est chargée de constater les infractions environnementales, y compris "
            "celles liées aux hydrocarbures. Cependant, il n'y a pas de précision sur la temporalité ou la "
            "fréquence des contrôles dans le contexte fourni."
        ),
        "relevant_keywords": ['période', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_044",
        "axe": 11,
        "axe_label": "Contrôle — zones",
        "question": (
            "Est-ce que au Congo, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction du rejet d'hydrocarbures ? Si ces procédures existent, vérifiez "
            "si elles précisent des lieux ou zones spécifiques pour le contrôle du respect de l'interdiction du "
            "rejet d'hydrocarbures."
        ),
        "country": "Congo",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Les procédures de contrôle pour garantir le respect de l'interdiction du rejet d'hydrocarbures sont "
            "décrites dans les articles 29 et 35 de la loi. Elles précisent que les rejets d'hydrocarbures "
            "doivent être autorisés par l'Autorité Maritime ou fluviale, mais il est spécifiquement indiqué que "
            "ces dispositions ne s'appliquent pas en cas d'urgence pour assurer la sécurité du navire ou éviter "
            "une avarie à la cargaison. Il n'y a aucune mention de lieux ou zones spécifiques pour le contrôle du "
            "respect de l'interdiction du rejet d'hydrocarbures dans les articles fournis."
        ),
        "relevant_keywords": ['zone', 'hydrocarbure'],
    },

    # --- Côte d'Ivoire ---

    {
        "id": "Q_HYD_045",
        "axe": 1,
        "axe_label": "Existence",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures en Côte d'Ivoire "
            "?"
        ),
        "country": "Côte d'Ivoire",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, il existe un article portant sur l'interdiction de rejet d'hydrocarbures en Côte d'Ivoire. Il "
            "s'agit de l'article premier du Code de l'environnement de la Côte d'Ivoire."
        ),
        "relevant_keywords": ['interdit', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_046",
        "axe": 2,
        "axe_label": "Zonage",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures en Côte d'Ivoire "
            "qui précise que cette mesure n'est applicable qu'à certaines zones, aires ou régions ?"
        ),
        "country": "Côte d'Ivoire",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Non, il n'existe pas d'article juridique portant sur l'interdiction du rejet d'hydrocarbures dans la "
            "zone fournie qui précise que cette mesure n'est applicable qu'à certaines zones, aires ou régions en "
            "Côte d'Ivoire."
        ),
        "relevant_keywords": ['zone', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_047",
        "axe": 3,
        "axe_label": "Temporalité",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures en Côte d'Ivoire "
            "qui précise que cette mesure n'est pas applicable en permanence (temporalité) ?"
        ),
        "country": "Côte d'Ivoire",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Non, il n'y a pas d'article juridique dans le contexte qui porte sur l'interdiction du rejet "
            "d'hydrocarbures avec une précision sur la temporalité en Côte d'Ivoire."
        ),
        "relevant_keywords": ['période', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_048",
        "axe": 4,
        "axe_label": "Types d\'activités concernées",
        "question": (
            "Est-ce que le texte juridique précise les types d'activités concernées par l'interdiction du rejet "
            "d'hydrocarbures en Côte d'Ivoire ?"
        ),
        "country": "Côte d'Ivoire",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, l'article 79 spécifie que les eaux usées et les déchets nuisibles ne peuvent pas être rejetés "
            "dans les eaux maritimes et lagunaires sous juridiction ivoirienne."
        ),
        "relevant_keywords": ['navire', 'rejet'],
    },

    {
        "id": "Q_HYD_049",
        "axe": 5,
        "axe_label": "Exceptions hors santé/ordre/recherche",
        "question": (
            "Est-ce que le texte juridique mentionne des exceptions à l'interdiction du rejet d'hydrocarbures en "
            "Côte d'Ivoire ? Vérifie si ce texte inclut des exceptions relatives à d'autres domaines que de la "
            "santé, de l'ordre public et de la recherche."
        ),
        "country": "Côte d'Ivoire",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Non, il n'y a pas d'exceptions mentionnées dans l'article juridique concernant l'interdiction de "
            "rejet d'hydrocarbures en Côte d'Ivoire."
        ),
        "relevant_keywords": [],
        "is_piege": True,
    },

    {
        "id": "Q_HYD_050",
        "axe": 6,
        "axe_label": "Exceptions / dérogations spécifiques",
        "question": (
            "Est-ce que le texte juridique mentionne des exceptions à l'interdiction du rejet d'hydrocarbures en "
            "Côte d'Ivoire ?"
        ),
        "country": "Côte d'Ivoire",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, l'article premier mentionne que le rejet d'hydrocarbures à la mer est interdit sauf dans les "
            "conditions définies par la Convention internationale de Londres du 2 novembre 1973, sur la "
            "prévention de la pollution par les navires, modifiée par le Protocole du 17 février 1978, en ses "
            "règles 9 et 11 de l'annexe I concernant la prévention de la pollution par les hydrocarbures "
            "(Convention MARPOL 73/78)."
        ),
        "relevant_keywords": ['dérogation', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_051",
        "axe": 7,
        "axe_label": "Sanction financière",
        "question": "Est-ce que le rejet d'hydrocarbures en Côte d'Ivoire entraîne une sanction financière (amende) ?",
        "country": "Côte d'Ivoire",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, selon l'article 100 du Code de l'environnement de la Côte d'Ivoire, le rejet d'hydrocarbures "
            "dans les eaux maritimes sous juridiction ivoirienne est puni d'une amende allant de 100.000.000 à 1 "
            "000.000.000 de francs."
        ),
        "relevant_keywords": ['amende', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_052",
        "axe": 8,
        "axe_label": "Sanction pénale",
        "question": "Est-ce que le rejet d'hydrocarbures en Côte d'Ivoire entraîne une peine de prison ?",
        "country": "Côte d'Ivoire",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, selon l'article 97 du Code de l'environnement de la Côte d'Ivoire, le rejet illégal "
            "d'hydrocarbures peut entraîner une peine de prison allant de six mois à deux ans."
        ),
        "relevant_keywords": ['emprisonnement', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_053",
        "axe": 9,
        "axe_label": "Contrôle — acteurs institutionnels",
        "question": (
            "Est-ce que en Côte d'Ivoire, des procédures de contrôle sont spécifiquement décrites pour garantir "
            "ou assurer le respect de l'interdiction du rejet d'hydrocarbures ?"
        ),
        "country": "Côte d'Ivoire",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, l'article 100 mentionne que \"l'administration maritime peut arraisonner tout navire surpris en "
            "flagrant délit de déversement de contaminants, y compris les hydrocarbures en mer\". Cela indique "
            "qu'il existe une administration pour superviser et constater l'application de cette interdiction."
        ),
        "relevant_keywords": ['administration', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_054",
        "axe": 10,
        "axe_label": "Contrôle — temporalité",
        "question": (
            "Est-ce que en Côte d'Ivoire, des procédures de contrôle sont spécifiquement décrites pour garantir "
            "ou assurer le respect de l'interdiction du rejet d'hydrocarbures ? Si ces procédures existent, "
            "vérifiez si elles précisent des périodes (temporalité) spécifiques pour le contrôle du respect de "
            "l'interdiction du rejet d'hydrocarbures."
        ),
        "country": "Côte d'Ivoire",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, l'article 100 de la loi-cadre nº 96-766 portant Code de l'environnement en Côte d'Ivoire "
            "prévoit que l'administration maritime peut arraisonner tout navire surpris en flagrant délit de "
            "déversement de contaminants, y compris les hydrocarbures en mer."
        ),
        "relevant_keywords": ['période', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_055",
        "axe": 11,
        "axe_label": "Contrôle — zones",
        "question": (
            "Est-ce que en Côte d'Ivoire, des procédures de contrôle sont spécifiquement décrites pour garantir "
            "ou assurer le respect de l'interdiction du rejet d'hydrocarbures ? Si ces procédures existent, "
            "vérifiez si elles précisent des lieux ou zones spécifiques pour le contrôle du respect de "
            "l'interdiction du rejet d'hydrocarbures."
        ),
        "country": "Côte d'Ivoire",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, l'article 100 de la loi-cadre nº 96-766 portant Code de l'environnement en Côte d'Ivoire "
            "prévoit que l'administration maritime peut arraisonner tout navire surpris en flagrant délit de "
            "déversement de contaminants, y compris les hydrocarbures en mer."
        ),
        "relevant_keywords": ['zone', 'hydrocarbure'],
    },

    # --- Djibouti ---

    {
        "id": "Q_HYD_056",
        "axe": 1,
        "axe_label": "Existence",
        "question": "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures à Djibouti ?",
        "country": "Djibouti",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, l'article 119 interdit le rejet d'hydrocarbures en mer par les navires sous pavillon de "
            "Djibouti ou se trouvant dans ses eaux territoriales et intérieures."
        ),
        "relevant_keywords": ['interdit', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_057",
        "axe": 2,
        "axe_label": "Zonage",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures à Djibouti qui "
            "précise que cette mesure n'est applicable qu'à certaines zones, aires ou régions ?"
        ),
        "country": "Djibouti",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Non. Il n'y a pas d'article dans le contexte portant sur l'interdiction du rejet d'hydrocarbures "
            "avec une précision quant aux zones applicables à Djibouti."
        ),
        "relevant_keywords": ['zone', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_058",
        "axe": 3,
        "axe_label": "Temporalité",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures à Djibouti qui "
            "précise que cette mesure n'est pas applicable en permanence (temporalité) ?"
        ),
        "country": "Djibouti",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Non, il n'y a pas d'article portant sur l'interdiction du rejet d'hydrocarbures qui précise une "
            "exception temporelle à Djibouti dans les documents fournis."
        ),
        "relevant_keywords": ['période', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_059",
        "axe": 4,
        "axe_label": "Types d\'activités concernées",
        "question": (
            "Est-ce que le texte juridique précise les types d'activités concernées par l'interdiction du rejet "
            "d'hydrocarbures à Djibouti ?"
        ),
        "country": "Djibouti",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, le texte juridique précise que les activités concernées par l'interdiction du rejet "
            "d'hydrocarbures sont celles relatives aux navires sous pavillon de Djibouti et aux navires étrangers "
            "se trouvant dans les eaux territoriales et intérieures de Djibouti, ainsi qu'aux plates-formes "
            "exploitées sur le plateau continental de Djibouti."
        ),
        "relevant_keywords": ['navire', 'rejet'],
    },

    {
        "id": "Q_HYD_060",
        "axe": 5,
        "axe_label": "Exceptions hors santé/ordre/recherche",
        "question": (
            "Est-ce que le texte juridique mentionne des exceptions à l'interdiction du rejet d'hydrocarbures à "
            "Djibouti ? Vérifie si ce texte inclut des exceptions relatives à d'autres domaines que de la santé, "
            "de l'ordre public et de la recherche."
        ),
        "country": "Djibouti",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, il y a une exception mentionnée dans l'article 126 qui concerne les navires djiboutiens soumis "
            "aux dispositions de la convention internationale pour la prévention de la pollution par les navires, "
            "entrant dans les catégories ci-après : Navires-citernes d’une jauge brute égale ou supérieure à 150 "
            "tonneaux ; Navires autres que navires-citernes d’une jauge brute égale ou supérieure à 500 tonneaux."
        ),
        "relevant_keywords": [],
        "is_piege": True,
    },

    {
        "id": "Q_HYD_061",
        "axe": 6,
        "axe_label": "Exceptions / dérogations spécifiques",
        "question": (
            "Est-ce que le texte juridique mentionne des exceptions à l'interdiction du rejet d'hydrocarbures à "
            "Djibouti ?"
        ),
        "country": "Djibouti",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, l'article 126 mentionne une exception pour les rejets effectués par un navire pour assurer sa "
            "propre sécurité ou celles d’autres navires, ou pour sauver des vies humaines, ainsi que pour les "
            "déversements résultant de dommages subis par le navire sans qu’aucune faute ne puisse être établie à "
            "l’encontre de son capitaine ou de son équipage."
        ),
        "relevant_keywords": ['dérogation', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_062",
        "axe": 7,
        "axe_label": "Sanction financière",
        "question": "Est-ce que le rejet d'hydrocarbures à Djibouti entraîne une sanction financière (amende) ?",
        "country": "Djibouti",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, selon l'article 119 du Code de l'Environnement de Djibouti, le rejet d'hydrocarbures en mer est "
            "punissable d'une amende allant d'un million à 10 millions de francs Djibouti."
        ),
        "relevant_keywords": ['amende', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_063",
        "axe": 8,
        "axe_label": "Sanction pénale",
        "question": "Est-ce que le rejet d'hydrocarbures à Djibouti entraîne une peine de prison ?",
        "country": "Djibouti",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, selon l'article 119 du Code de l'Environnement de Djibouti, le rejet d'hydrocarbures en mer "
            "peut entraîner une peine d'emprisonnement allant de un an à trois ans pour le capitaine du navire "
            "responsable."
        ),
        "relevant_keywords": ['emprisonnement', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_064",
        "axe": 9,
        "axe_label": "Contrôle — acteurs institutionnels",
        "question": (
            "Est-ce que à Djibouti, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction du rejet d'hydrocarbures ?"
        ),
        "country": "Djibouti",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, l'article 23 stipule que les déversements, immersions et incinérations dans les eaux marines "
            "sous juridiction djiboutienne des substances susceptibles de porter atteinte aux ressources marines "
            "physiques et biologiques sont interdits."
        ),
        "relevant_keywords": ['administration', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_065",
        "axe": 10,
        "axe_label": "Contrôle — temporalité",
        "question": (
            "Est-ce que à Djibouti, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction du rejet d'hydrocarbures ? Si ces procédures existent, vérifiez "
            "si elles précisent des périodes (temporalité) spécifiques pour le contrôle du respect de "
            "l'interdiction du rejet d'hydrocarbures."
        ),
        "country": "Djibouti",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Il n'y a pas de mention spécifique dans les articles fournis concernant des procédures de contrôle "
            "dédiées pour garantir ou assurer le respect de l'interdiction du rejet d'hydrocarbures à Djibouti."
        ),
        "relevant_keywords": ['période', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_066",
        "axe": 11,
        "axe_label": "Contrôle — zones",
        "question": (
            "Est-ce que à Djibouti, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction du rejet d'hydrocarbures ? Si ces procédures existent, vérifiez "
            "si elles précisent des lieux ou zones spécifiques pour le contrôle du respect de l'interdiction du "
            "rejet d'hydrocarbures."
        ),
        "country": "Djibouti",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, à Djibouti, il existe des procédures de contrôle spécifiques pour garantir le respect de "
            "l'interdiction du rejet d'hydrocarbures. L'article 23 stipule que les déversements, immersions et "
            "incinérations dans les eaux marines sous juridiction djiboutienne des substances susceptibles de "
            "nuire à la santé humaine et aux activités maritimes et touristiques sont interdits. Les articles 119 "
            "et 126 prévoient des sanctions pour les capitaines de navires se rendant coupables d'un rejet en mer "
            "d'hydrocarbures ou d'autres substances liquides nocives pour le milieu marin, en infraction avec les "
            "dispositions du présent Code et des règlements pris pour son application. Les articles 20 et 134 "
            "prévoient également des mesures réglementaires déterminant les conditions de rejet et les conditions "
            "d'analyse et de contrôle des prélèvements des rejets."
        ),
        "relevant_keywords": ['zone', 'hydrocarbure'],
    },

    # --- Gabon ---

    {
        "id": "Q_HYD_067",
        "axe": 1,
        "axe_label": "Existence",
        "question": "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures au Gabon ?",
        "country": "Gabon",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, l'article 151 interdit le déversement ou le rejet intentionnel d’hydrocarbures en mer ou sur "
            "terre."
        ),
        "relevant_keywords": ['interdit', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_068",
        "axe": 2,
        "axe_label": "Zonage",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures au Gabon qui "
            "précise que cette mesure n'est applicable qu'à certaines zones, aires ou régions ?"
        ),
        "country": "Gabon",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Non, il n'y a pas d'article portant sur l'interdiction du rejet d'hydrocarbures qui précise que "
            "cette mesure n'est applicable qu'à certaines zones, aires ou régions au Gabon dans les documents "
            "fournis."
        ),
        "relevant_keywords": ['zone', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_069",
        "axe": 3,
        "axe_label": "Temporalité",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures au Gabon qui "
            "précise que cette mesure n'est pas applicable en permanence (temporalité) ?"
        ),
        "country": "Gabon",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Non, il n'y a pas d'article portant sur l'interdiction du rejet d'hydrocarbures avec une précision "
            "sur la temporalité au Gabon dans le contexte fourni."
        ),
        "relevant_keywords": ['période', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_070",
        "axe": 4,
        "axe_label": "Types d\'activités concernées",
        "question": (
            "Est-ce que le texte juridique précise les types d'activités concernées par l'interdiction du rejet "
            "d'hydrocarbures au Gabon ?"
        ),
        "country": "Gabon",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, l'article 151 de la loi gabonaise relative à la protection de l'environnement précise que le "
            "déversement ou le rejet intentionnel d’hydrocarbures en mer ou sur terre est interdit."
        ),
        "relevant_keywords": ['navire', 'rejet'],
    },

    {
        "id": "Q_HYD_071",
        "axe": 5,
        "axe_label": "Exceptions hors santé/ordre/recherche",
        "question": (
            "Est-ce que le texte juridique mentionne des exceptions à l'interdiction du rejet d'hydrocarbures au "
            "Gabon ? Vérifie si ce texte inclut des exceptions relatives à d'autres domaines que de la santé, de "
            "l'ordre public et de la recherche."
        ),
        "country": "Gabon",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Non, il n'y a pas d'exceptions mentionnées dans le texte juridique concernant l'interdiction du "
            "rejet d'hydrocarbures au Gabon, à part les cas où l'activité considérée est conforme aux normes "
            "légales et ne nuise pas à la santé humaine ou au maintien de l'équilibre biologique des eaux."
        ),
        "relevant_keywords": [],
        "is_piege": True,
    },

    {
        "id": "Q_HYD_072",
        "axe": 6,
        "axe_label": "Exceptions / dérogations spécifiques",
        "question": (
            "Est-ce que le texte juridique mentionne des exceptions à l'interdiction du rejet d'hydrocarbures au "
            "Gabon ?"
        ),
        "country": "Gabon",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, l'article 151 mentionne une exception pour le rejet intentionnel d'hydrocarbures en mer ou sur "
            "terre, qui est punissable si elle n'est pas autorisée."
        ),
        "relevant_keywords": ['dérogation', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_073",
        "axe": 7,
        "axe_label": "Sanction financière",
        "question": "Est-ce que le rejet d'hydrocarbures au Gabon entraîne une sanction financière (amende) ?",
        "country": "Gabon",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, selon l'article 59 de la loi gabonaise n°007/2014 relative à la protection de l'environnement, "
            "le rejet d'hydrocarbures dans les eaux maritimes nationales est interdit et peut entraîner une "
            "sanction financière (amende)."
        ),
        "relevant_keywords": ['amende', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_074",
        "axe": 8,
        "axe_label": "Sanction pénale",
        "question": "Est-ce que le rejet d'hydrocarbures au Gabon entraîne une peine de prison ?",
        "country": "Gabon",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, selon l'article 151 de la loi gabonaise relative à la protection de l'environnement, le "
            "déversement ou le rejet intentionnel d’hydrocarbures en mer ou sur terre est puni d'un "
            "emprisonnement de six mois à cinq ans ou de l’une de ces deux peines seulement."
        ),
        "relevant_keywords": ['emprisonnement', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_075",
        "axe": 9,
        "axe_label": "Contrôle — acteurs institutionnels",
        "question": (
            "Est-ce que au Gabon, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction du rejet d'hydrocarbures ?"
        ),
        "country": "Gabon",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, au Gabon, des procédures de contrôle sont spécifiquement décrites pour garantir ou assurer le "
            "respect de l'interdiction du rejet d'hydrocarbures. L'article 59 de la loi n° 007/2014 relative à la "
            "protection de l'environnement en République gabonaise interdit le déversement, l'immersion et "
            "l'incinération dans les eaux maritimes nationales de substances dont la liste est fixée par voie "
            "réglementaire et qui sont susceptibles de porter atteinte à la santé de l'homme et aux ressources "
            "biologiques maritimes. Le ministre en charge de l'Environnement exerce un contrôle régulier pour "
            "vérifier que ces prescriptions sont respectées, conformément à l'article 35 de la même loi. En cas "
            "de non-respect de ces prescriptions, le ministre peut suspendre ou retirer l'autorisation prévue à "
            "l'article 34."
        ),
        "relevant_keywords": ['administration', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_076",
        "axe": 10,
        "axe_label": "Contrôle — temporalité",
        "question": (
            "Est-ce que au Gabon, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction du rejet d'hydrocarbures ? Si ces procédures existent, vérifiez "
            "si elles précisent des périodes (temporalité) spécifiques pour le contrôle du respect de "
            "l'interdiction du rejet d'hydrocarbures."
        ),
        "country": "Gabon",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, au Gabon, il existe une administration spécifique en charge de l'environnement qui peut exercer "
            "un contrôle régulier pour vérifier que les prescriptions légales sont respectées (Article 35). Cette "
            "administration peut suspendre ou retirer l'autorisation de rejet d'hydrocarbures en cas de "
            "non-respect des prescriptions. Cependant, le contexte ne précise pas si ces contrôles sont effectués "
            "à des périodes spécifiques."
        ),
        "relevant_keywords": ['période', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_077",
        "axe": 11,
        "axe_label": "Contrôle — zones",
        "question": (
            "Est-ce que au Gabon, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction du rejet d'hydrocarbures ? Si ces procédures existent, vérifiez "
            "si elles précisent des lieux ou zones spécifiques pour le contrôle du respect de l'interdiction du "
            "rejet d'hydrocarbures."
        ),
        "country": "Gabon",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, au Gabon, il existe une administration spécifique chargée de vérifier que les prescriptions "
            "relatives à l'autorisation de rejeter des substances dans les eaux maritimes sont respectées "
            "(Article 35). Cette administration peut suspendre ou retirer l'autorisation en cas de non-respect "
            "des prescriptions. Cependant, le contexte ne spécifie pas si cette administration est dédiée "
            "uniquement aux hydrocarbures ou si elle s'occupe également d'autres substances."
        ),
        "relevant_keywords": ['zone', 'hydrocarbure'],
    },

    # --- Guinée ---

    {
        "id": "Q_HYD_078",
        "axe": 1,
        "axe_label": "Existence",
        "question": "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures en Guinée ?",
        "country": "Guinée",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, il existe un article portant sur l'interdiction du rejet d'hydrocarbures en Guinée : ARTICLE 14 "
            "- Aux fins de l'application de l'article 33 de l'Ordonnance n° 045/PRG/87 du Mai 1987, portant Code "
            "de l'Environnement, le rejet d'hydrocarbures par tout navire dans les zones maritimes guinéennes est "
            "interdit sauf lorsque toutes les conditions suivantes se trouvent réunies..."
        ),
        "relevant_keywords": ['interdit', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_079",
        "axe": 2,
        "axe_label": "Zonage",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures en Guinée qui "
            "précise que cette mesure n'est applicable qu'à certaines zones, aires ou régions ?"
        ),
        "country": "Guinée",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, l'article 14 spécifie les conditions dans lesquelles le rejet d'hydrocarbures est autorisé, "
            "notamment lorsqu'il est effectué par un pétrolier en route et à plus de 50 milles marins de la côte "
            "guinéenne la plus proche."
        ),
        "relevant_keywords": ['zone', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_080",
        "axe": 3,
        "axe_label": "Temporalité",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures en Guinée qui "
            "précise que cette mesure n'est pas applicable en permanence (temporalité) ?"
        ),
        "country": "Guinée",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Non, il n'y a pas d'article dans le contexte fourni qui mentionne explicitement que l'interdiction "
            "du rejet d'hydrocarbures en Guinée n'est pas applicable en permanence."
        ),
        "relevant_keywords": ['période', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_081",
        "axe": 4,
        "axe_label": "Types d\'activités concernées",
        "question": (
            "Est-ce que le texte juridique précise les types d'activités concernées par l'interdiction du rejet "
            "d'hydrocarbures en Guinée ?"
        ),
        "country": "Guinée",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, le texte juridique précise les types d'activités concernées par l'interdiction du rejet "
            "d'hydrocarbures en Guinée. Selon l'Article 14, il est interdit aux pétroliers et aux autres navires "
            "d'une jauge brute égale ou supérieure à 400 tonneaux de rejeter des hydrocarbures dans les zones "
            "maritimes guinéennes, sauf si certaines conditions sont réunies."
        ),
        "relevant_keywords": ['navire', 'rejet'],
    },

    {
        "id": "Q_HYD_082",
        "axe": 5,
        "axe_label": "Exceptions hors santé/ordre/recherche",
        "question": (
            "Est-ce que le texte juridique mentionne des exceptions à l'interdiction du rejet d'hydrocarbures en "
            "Guinée ? Vérifie si ce texte inclut des exceptions relatives à d'autres domaines que de la santé, de "
            "l'ordre public et de la recherche."
        ),
        "country": "Guinée",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, il y a des exceptions mentionnées dans l'article 60 du Code de l'Environnement guinéen. Ces "
            "exceptions incluent les substances déversées en mer dans le cadre d'opérations de lutte contre la "
            "pollution marine par les hydrocarbures menées par les autorités compétentes ou par toute autre "
            "personne habilitée à cet effet, ainsi que les déversements effectués en cas de force majeure lorsque "
            "la sécurité d'un navire ou de ses occupants est gravement menacée."
        ),
        "relevant_keywords": [],
        "is_piege": True,
    },

    {
        "id": "Q_HYD_083",
        "axe": 6,
        "axe_label": "Exceptions / dérogations spécifiques",
        "question": (
            "Est-ce que le texte juridique mentionne des exceptions à l'interdiction du rejet d'hydrocarbures en "
            "Guinée ?"
        ),
        "country": "Guinée",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, il y a des exceptions à l'interdiction du rejet d'hydrocarbures en Guinée. Selon l'article 14, "
            "les pétroliers peuvent rejeter des hydrocarbures dans certaines conditions spécifiques, telles que "
            "la distance de la côte et la quantité rejetée. De plus, l'article 60 prévoit des exceptions pour les "
            "opérations de lutte contre la pollution marine par les hydrocarbures menées par les autorités "
            "guinéennes compétentes ou par toute autre personne habilitée à cet effet, ainsi que pour les "
            "déversements effectués en cas de force majeure lorsque la sécurité d'un navire ou de ses occupants "
            "est gravement menacée."
        ),
        "relevant_keywords": ['dérogation', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_084",
        "axe": 7,
        "axe_label": "Sanction financière",
        "question": "Est-ce que le rejet d'hydrocarbures en Guinée entraîne une sanction financière (amende) ?",
        "country": "Guinée",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, selon l'article 184 du Code maritime guinéen, le capitaine de navire qui aura rejeté des "
            "hydrocarbures en violation des dispositions des textes réglementaires en vigueur est puni d'une "
            "amende allant de 10.000.000.000 GNF à 100.000.000.000 GNF."
        ),
        "relevant_keywords": ['amende', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_085",
        "axe": 8,
        "axe_label": "Sanction pénale",
        "question": "Est-ce que le rejet d'hydrocarbures en Guinée entraîne une peine de prison ?",
        "country": "Guinée",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, selon l'article 889 du Code maritime guinéen, le capitaine d'un navire guinéen entrant dans les "
            "catégories suivantes et soumis aux dispositions de l'Annexe I de MARPOL relatives aux interdictions "
            "de rejets d'hydrocarbures, qui se rend coupable d'infractions à ses règles 9 et 10, est passible "
            "d'une amende de 5.000.000 à 50.000.000 € et d'un emprisonnement de 1 à 5 ans, ou de l'une de ces "
            "deux peines seulement."
        ),
        "relevant_keywords": ['emprisonnement', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_086",
        "axe": 9,
        "axe_label": "Contrôle — acteurs institutionnels",
        "question": (
            "Est-ce que en Guinée, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction du rejet d'hydrocarbures ?"
        ),
        "country": "Guinée",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, l'article 34 décrit des procédures de contrôle pour garantir le respect de l'interdiction du "
            "rejet d'hydrocarbures en Guinée. Les autorités civiles et militaires chargées du contrôle des zones "
            "maritimes guinéennes peuvent procéder à une inspection matérielle du navire si elles ont de "
            "sérieuses raisons de penser qu'un navire a commis une infraction entraînant une pollution notable."
        ),
        "relevant_keywords": ['administration', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_087",
        "axe": 10,
        "axe_label": "Contrôle — temporalité",
        "question": (
            "Est-ce que en Guinée, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction du rejet d'hydrocarbures ? Si ces procédures existent, vérifiez "
            "si elles précisent des périodes (temporalité) spécifiques pour le contrôle du respect de "
            "l'interdiction du rejet d'hydrocarbures."
        ),
        "country": "Guinée",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, il existe des procédures de contrôle spécifiquement décrites pour garantir ou assurer le "
            "respect de l'interdiction du rejet d'hydrocarbures en Guinée. L'Article 13 stipule que la Direction "
            "de la Marine Marchande est chargée de réaliser des visites périodiques destinées à prévenir les "
            "risques de pollution des zones maritimes guinéennes. Un arrêté du Ministre chargé des Transports "
            "Maritimes fixe les prescriptions à respecter en matière de contrôle de la pollution et le détail de "
            "ces visites. Le procès-verbal de ces dernières est transmis à la Direction de l'Environnement."
        ),
        "relevant_keywords": ['période', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_088",
        "axe": 11,
        "axe_label": "Contrôle — zones",
        "question": (
            "Est-ce que en Guinée, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction du rejet d'hydrocarbures ? Si ces procédures existent, vérifiez "
            "si elles précisent des lieux ou zones spécifiques pour le contrôle du respect de l'interdiction du "
            "rejet d'hydrocarbures."
        ),
        "country": "Guinée",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, il existe des procédures de contrôle spécifiquement décrites pour garantir le respect de "
            "l'interdiction du rejet d'hydrocarbures en Guinée. L'ARTICLE 13 stipule que la Direction de la "
            "Marine Marchande est chargée de réaliser des visites périodiques sur les pétroliers et autres "
            "navires d'une jauge brute égale ou supérieure à 400 tonneaux pour prévenir les risques de pollution "
            "des zones maritimes guinéennes. Un arrêté du Ministre chargé des Transports Maritimes fixe les "
            "prescriptions à respecter en matière de contrôle de la pollution et le détail de ces visites. Le "
            "procès-verbal de ces dernières est transmis à la Direction de l'Environnement."
        ),
        "relevant_keywords": ['zone', 'hydrocarbure'],
    },

    # --- Maroc ---

    {
        "id": "Q_HYD_089",
        "axe": 1,
        "axe_label": "Existence",
        "question": "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures au Maroc ?",
        "country": "Maroc",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, l'article 6 stipule que seuls les rejets d'hydrocarbures ou de mélanges d'hydrocarbures "
            "effectués dans des conditions fixées par voie réglementaire ne sont pas considérés comme des rejets "
            "interdits."
        ),
        "relevant_keywords": ['interdit', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_090",
        "axe": 2,
        "axe_label": "Zonage",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures au Maroc qui "
            "précise que cette mesure n'est applicable qu'à certaines zones, aires ou régions ?"
        ),
        "country": "Maroc",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "L'Article 3 précise que les dispositions s'appliquent aux eaux maritimes marocaines visées à "
            "l'article 2 et aux navires battant pavillon étranger lorsqu'ils effectuent des rejets dans ces eaux."
        ),
        "relevant_keywords": ['zone', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_091",
        "axe": 3,
        "axe_label": "Temporalité",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures au Maroc qui "
            "précise que cette mesure n'est pas applicable en permanence (temporalité) ?"
        ),
        "country": "Maroc",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Non, il n'y a pas d'article spécifique dans le contexte fourni qui indique une exemption permanente "
            "de l'interdiction de rejeter des hydrocarbures au Maroc."
        ),
        "relevant_keywords": ['période', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_092",
        "axe": 4,
        "axe_label": "Types d\'activités concernées",
        "question": (
            "Est-ce que le texte juridique précise les types d'activités concernées par l'interdiction du rejet "
            "d'hydrocarbures au Maroc ?"
        ),
        "country": "Maroc",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, le texte juridique précise que seuls les rejets d'hydrocarbures ou de mélanges d'hydrocarbures "
            "effectués dans les conditions et selon les modalités fixées par voie réglementaire et qui tiennent "
            "compte des dispositions de l’annexe I de la Convention MARPOL ne sont pas considérés comme des "
            "rejets interdits."
        ),
        "relevant_keywords": ['navire', 'rejet'],
    },

    {
        "id": "Q_HYD_093",
        "axe": 5,
        "axe_label": "Exceptions hors santé/ordre/recherche",
        "question": (
            "Est-ce que le texte juridique mentionne des exceptions à l'interdiction du rejet d'hydrocarbures au "
            "Maroc ? Vérifie si ce texte inclut des exceptions relatives à d'autres domaines que de la santé, de "
            "l'ordre public et de la recherche."
        ),
        "country": "Maroc",
        "theme": "rejets_hydrocarbures",
        "ground_truth": "Oui, l'article 5 mentionne des exceptions à l'interdiction du rejet d'hydrocarbures au Maroc.",
        "relevant_keywords": [],
        "is_piege": True,
    },

    {
        "id": "Q_HYD_094",
        "axe": 6,
        "axe_label": "Exceptions / dérogations spécifiques",
        "question": (
            "Est-ce que le texte juridique mentionne des exceptions à l'interdiction du rejet d'hydrocarbures au "
            "Maroc ?"
        ),
        "country": "Maroc",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, l'article 6 mentionne une exception pour les rejets d'hydrocarbures effectués dans les "
            "conditions et selon les modalités fixées par voie réglementaire et qui tiennent compte des "
            "dispositions de l’annexe I de la Convention MARPOL."
        ),
        "relevant_keywords": ['dérogation', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_095",
        "axe": 7,
        "axe_label": "Sanction financière",
        "question": "Est-ce que le rejet d'hydrocarbures au Maroc entraîne une sanction financière (amende) ?",
        "country": "Maroc",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, selon l'article 6 de la loi marocaine n° 69-18 relative à la pollution par les navires, seuls "
            "les rejets d'hydrocarbures effectués dans des conditions spécifiques et réglementées ne sont pas "
            "considérés comme des rejets interdits. Cependant, si ces rejets contiennent des quantités ou des "
            "concentrations de produits chimiques dangereux pour le milieu marin ou des substances ajoutées pour "
            "contourner les conditions de rejet, ils peuvent entraîner une amende allant de 50 000 à 150 000 "
            "dirhams (article 44)."
        ),
        "relevant_keywords": ['amende', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_096",
        "axe": 8,
        "axe_label": "Sanction pénale",
        "question": "Est-ce que le rejet d'hydrocarbures au Maroc entraîne une peine de prison ?",
        "country": "Maroc",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, selon l'article 45, le rejet d'hydrocarbures peut entraîner une peine d'emprisonnement allant "
            "de trois ans à sept ans."
        ),
        "relevant_keywords": ['emprisonnement', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_097",
        "axe": 9,
        "axe_label": "Contrôle — acteurs institutionnels",
        "question": (
            "Est-ce que au Maroc, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction du rejet d'hydrocarbures ?"
        ),
        "country": "Maroc",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, au Maroc, des procédures de contrôle sont spécifiquement décrites pour garantir ou assurer le "
            "respect de l'interdiction du rejet d'hydrocarbures. L'article 34 prévoit que tout capitaine de "
            "navire doit informer immédiatement l'autorité compétente en cas de rejet d'hydrocarbures dans les "
            "eaux maritimes marocaines."
        ),
        "relevant_keywords": ['administration', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_098",
        "axe": 10,
        "axe_label": "Contrôle — temporalité",
        "question": (
            "Est-ce que au Maroc, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction du rejet d'hydrocarbures ? Si ces procédures existent, vérifiez "
            "si elles précisent des périodes (temporalité) spécifiques pour le contrôle du respect de "
            "l'interdiction du rejet d'hydrocarbures."
        ),
        "country": "Maroc",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, au Maroc, il existe des procédures de contrôle spécifiquement décrites pour garantir ou assurer "
            "le respect de l'interdiction du rejet d'hydrocarbures. L'article 34 de la loi n°69-18 relative à la "
            "pollution par les navires prévoit que tout capitaine d’un navire navigant dans les eaux maritimes "
            "marocaines doit informer immédiatement l’autorité compétente en cas de rejet de polluants dans ces "
            "eaux. Cette obligation s'applique également aux capitaines ayant connaissance d'un tel incident ou "
            "événement. L'article 35 prévoit que le propriétaire ou l'exploitant du navire source de ce rejet est "
            "mis en demeure par l'autorité compétente pour prendre toutes les mesures nécessaires pour mettre fin "
            "audit rejet dans les conditions qu’elle fixe. En cas d’urgence, la mise en demeure est faite au "
            "capitaine du navire ou à la personne ayant la charge du navire en cas d’indisponibilité du "
            "capitaine."
        ),
        "relevant_keywords": ['période', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_099",
        "axe": 11,
        "axe_label": "Contrôle — zones",
        "question": (
            "Est-ce que au Maroc, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction du rejet d'hydrocarbures ? Si ces procédures existent, vérifiez "
            "si elles précisent des lieux ou zones spécifiques pour le contrôle du respect de l'interdiction du "
            "rejet d'hydrocarbures."
        ),
        "country": "Maroc",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, au Maroc, il existe des procédures de contrôle spécifiquement décrites pour garantir le respect "
            "de l'interdiction du rejet d'hydrocarbures. L'article 34 stipule que tout capitaine d’un navire "
            "navigant dans les eaux maritimes marocaines doit informer immédiatement l'autorité compétente en cas "
            "de rejet de polluants. L'article 32 prévoit également que tout capitaine ou toute autre personne "
            "ayant la charge du navire doit informer immédiatement l'autorité compétente en cas d'incident "
            "technique susceptible d'entraîner une pollution des eaux maritimes marocaines. Ces procédures sont "
            "décrites dans la loi n° 69-18 relative à la pollution par les navires, promulguée par le Dahir n° "
            "1-21-25 du 10 rejeb 1442 (22 février 2021)."
        ),
        "relevant_keywords": ['zone', 'hydrocarbure'],
    },

    # --- Mauritanie ---

    {
        "id": "Q_HYD_100",
        "axe": 1,
        "axe_label": "Existence",
        "question": "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures en Mauritanie ?",
        "country": "Mauritanie",
        "theme": "rejets_hydrocarbures",
        "ground_truth": "Oui, l'article 284 porte sur l'interdiction du rejet d'hydrocarbures en Mauritanie.",
        "relevant_keywords": ['interdit', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_101",
        "axe": 2,
        "axe_label": "Zonage",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures en Mauritanie qui "
            "précise que cette mesure n'est applicable qu'à certaines zones, aires ou régions ?"
        ),
        "country": "Mauritanie",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Non, il n'y a pas d'article portant spécifiquement sur une interdiction du rejet d'hydrocarbures "
            "applicable uniquement à certaines zones, aires ou régions en Mauritanie dans le contexte fourni."
        ),
        "relevant_keywords": ['zone', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_102",
        "axe": 3,
        "axe_label": "Temporalité",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures en Mauritanie qui "
            "précise que cette mesure n'est pas applicable en permanence (temporalité) ?"
        ),
        "country": "Mauritanie",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Non, il n'y a pas d'article juridique trouvé dans le contexte qui porte sur une interdiction du "
            "rejet d'hydrocarbures avec une précision temporelle en Mauritanie."
        ),
        "relevant_keywords": ['période', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_103",
        "axe": 4,
        "axe_label": "Types d\'activités concernées",
        "question": (
            "Est-ce que le texte juridique précise les types d'activités concernées par l'interdiction du rejet "
            "d'hydrocarbures en Mauritanie ?"
        ),
        "country": "Mauritanie",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, le texte juridique précise les types d'activités concernées par l'interdiction du rejet "
            "d'hydrocarbures en Mauritanie. Selon l'ARTICLE 284, il est interdit de rejeter des hydrocarbures ou "
            "des mélanges d'hydrocarbures susceptible de porter atteinte à la faune et à la flore marine, à la "
            "santé publique et au développement économique touristique des régions côtières conformément aux "
            "dispositions de MARPOL 73/78."
        ),
        "relevant_keywords": ['navire', 'rejet'],
    },

    {
        "id": "Q_HYD_104",
        "axe": 5,
        "axe_label": "Exceptions hors santé/ordre/recherche",
        "question": (
            "Est-ce que le texte juridique mentionne des exceptions à l'interdiction du rejet d'hydrocarbures en "
            "Mauritanie ? Vérifie si ce texte inclut des exceptions relatives à d'autres domaines que de la "
            "santé, de l'ordre public et de la recherche."
        ),
        "country": "Mauritanie",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, l'article 256 mentionne plusieurs exceptions à l'interdiction du rejet d'hydrocarbures en mer, "
            "notamment pour assurer la sécurité du navire ou sauver des vies humaines, pour lutter contre une "
            "pollution avec l'approbation de l'Autorité maritime, et en cas de force majeure."
        ),
        "relevant_keywords": [],
        "is_piege": True,
    },

    {
        "id": "Q_HYD_105",
        "axe": 6,
        "axe_label": "Exceptions / dérogations spécifiques",
        "question": (
            "Est-ce que le texte juridique mentionne des exceptions à l'interdiction du rejet d'hydrocarbures en "
            "Mauritanie ?"
        ),
        "country": "Mauritanie",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, l'article 256 mentionne plusieurs exceptions à l'interdiction du rejet d'hydrocarbures en "
            "Mauritanie."
        ),
        "relevant_keywords": ['dérogation', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_106",
        "axe": 7,
        "axe_label": "Sanction financière",
        "question": "Est-ce que le rejet d'hydrocarbures en Mauritanie entraîne une sanction financière (amende) ?",
        "country": "Mauritanie",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, selon l'article 657 du code de la Marine marchande mauritanien, le rejet d'hydrocarbures est "
            "passible d'une amende allant de 5 000 000 à 50 000 000 UM."
        ),
        "relevant_keywords": ['amende', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_107",
        "axe": 8,
        "axe_label": "Sanction pénale",
        "question": "Est-ce que le rejet d'hydrocarbures en Mauritanie entraîne une peine de prison ?",
        "country": "Mauritanie",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, selon l'article 657 du code de la Marine marchande mauritanien, le capitaine d'un navire "
            "mauritanien entrant dans les catégories suivantes et soumis aux dispositions de l'annexe I de MARPOL "
            "73/78 relative aux interdictions de rejets d'hydrocarbures, qui se rend coupable d'infractions à ses "
            "règles 9 et 10, est passible d'un emprisonnement de 1 an à 5 ans."
        ),
        "relevant_keywords": ['emprisonnement', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_108",
        "axe": 9,
        "axe_label": "Contrôle — acteurs institutionnels",
        "question": (
            "Est-ce que en Mauritanie, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction du rejet d'hydrocarbures ?"
        ),
        "country": "Mauritanie",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, les articles 642 et 657-658 du Code de la Marine marchande mauritanien décrivent des procédures "
            "de contrôle spécifiques pour garantir ou assurer le respect de l'interdiction du rejet "
            "d'hydrocarbures en Mauritanie. Ces articles prévoient notamment l'intervention d'agents habilités, "
            "tels que les agents du Ministère chargé de la Marine marchande, les Commandants et Commandants en "
            "second des bâtiments de la Marine nationale, les Gendarmes maritimes, etc., pour rechercher et "
            "constater les infractions en matière de pollution marine."
        ),
        "relevant_keywords": ['administration', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_109",
        "axe": 10,
        "axe_label": "Contrôle — temporalité",
        "question": (
            "Est-ce que en Mauritanie, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction du rejet d'hydrocarbures ? Si ces procédures existent, vérifiez "
            "si elles précisent des périodes (temporalité) spécifiques pour le contrôle du respect de "
            "l'interdiction du rejet d'hydrocarbures."
        ),
        "country": "Mauritanie",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, les articles 642 et 657-658 spécifient que des agents habilités tels que les Commandants de "
            "bâtiments de la Marine nationale, les Gendarmes maritimes, les Capitaines et Officiers de port, les "
            "agents de l'administration des Douanes, etc., sont compétents pour rechercher et constater les "
            "infractions en matière de pollution marine, y compris le rejet d'hydrocarbures. Les articles 657-658 "
            "précisent également que ces agents peuvent infliger des amendes et des peines d'emprisonnement aux "
            "capitaines de navires mauritaniens qui enfreignent les règles MARPOL relatives aux rejets "
            "d'hydrocarbures. Cependant, il n'y a pas de précision sur la temporalité ou la périodicité de ces "
            "contrôles dans le contexte fourni."
        ),
        "relevant_keywords": ['période', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_110",
        "axe": 11,
        "axe_label": "Contrôle — zones",
        "question": (
            "Est-ce que en Mauritanie, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction du rejet d'hydrocarbures ? Si ces procédures existent, vérifiez "
            "si elles précisent des lieux ou zones spécifiques pour le contrôle du respect de l'interdiction du "
            "rejet d'hydrocarbures."
        ),
        "country": "Mauritanie",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, les articles 642 et 657 de la loi mauritanienne n° 2013-029 portant code de la Marine marchande "
            "prévoient des procédures de contrôle spécifiques pour garantir le respect de l'interdiction du rejet "
            "d'hydrocarbures. Ces procédures incluent notamment les agents habilités du Ministère chargé de la "
            "Marine marchande, les Commandants et Commandants en second des bâtiments de la Marine nationale ou "
            "les aéronefs de guerre, les Gendarmes maritimes, les Capitaines et Officiers de port, ainsi que les "
            "agents de l'administration des Douanes. Ces agents sont habilités à rechercher et constater les "
            "infractions en matière de pollution marine, y compris le rejet d'hydrocarbures. L'article 657 "
            "prévoit également des sanctions pour les capitaines de navires mauritaniens qui se rendraient "
            "coupables d'infractions aux règles 9 et 10 de l'annexe I de MARPOL 73/78 relative aux interdictions "
            "de rejets d'hydrocarbures."
        ),
        "relevant_keywords": ['zone', 'hydrocarbure'],
    },

    # --- Sénégal ---

    {
        "id": "Q_HYD_111",
        "axe": 1,
        "axe_label": "Existence",
        "question": "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures au Sénégal ?",
        "country": "Sénégal",
        "theme": "rejets_hydrocarbures",
        "ground_truth": "Oui, l'article 211 interdit le rejet d'hydrocarbures en mer au Sénégal.",
        "relevant_keywords": ['interdit', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_112",
        "axe": 2,
        "axe_label": "Zonage",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures au Sénégal qui "
            "précise que cette mesure n'est applicable qu'à certaines zones, aires ou régions ?"
        ),
        "country": "Sénégal",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Non, il n'y a pas d'article portant sur l'interdiction du rejet d'hydrocarbures qui précise que "
            "cette mesure n'est applicable qu'à certaines zones, aires ou régions au Sénégal dans les documents "
            "fournis."
        ),
        "relevant_keywords": ['zone', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_113",
        "axe": 3,
        "axe_label": "Temporalité",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures au Sénégal qui "
            "précise que cette mesure n'est pas applicable en permanence (temporalité) ?"
        ),
        "country": "Sénégal",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Non, il n'y a pas d'article portant sur l'interdiction du rejet d'hydrocarbures qui précise une "
            "exception temporelle au Sénégal dans le contexte fourni."
        ),
        "relevant_keywords": ['période', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_114",
        "axe": 4,
        "axe_label": "Types d\'activités concernées",
        "question": (
            "Est-ce que le texte juridique précise les types d'activités concernées par l'interdiction du rejet "
            "d'hydrocarbures au Sénégal ?"
        ),
        "country": "Sénégal",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, le texte juridique précise que l'interdiction du rejet d'hydrocarbures s'applique "
            "spécifiquement aux navires transportant une cargaison de plus de deux mille tonnes d'hydrocarbures "
            "en vrac transitant dans les eaux territoriales ou dans les ports sénégalais (Art. 161)."
        ),
        "relevant_keywords": ['navire', 'rejet'],
    },

    {
        "id": "Q_HYD_115",
        "axe": 5,
        "axe_label": "Exceptions hors santé/ordre/recherche",
        "question": (
            "Est-ce que le texte juridique mentionne des exceptions à l'interdiction du rejet d'hydrocarbures au "
            "Sénégal ? Vérifie si ce texte inclut des exceptions relatives à d'autres domaines que de la santé, "
            "de l'ordre public et de la recherche."
        ),
        "country": "Sénégal",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, il y a une exception mentionnée dans l'article 133 : \"dans le cadre des opérations "
            "d'exploration, de tests de puits et de maintenance\"."
        ),
        "relevant_keywords": [],
        "is_piege": True,
    },

    {
        "id": "Q_HYD_116",
        "axe": 6,
        "axe_label": "Exceptions / dérogations spécifiques",
        "question": (
            "Est-ce que le texte juridique mentionne des exceptions à l'interdiction du rejet d'hydrocarbures au "
            "Sénégal ?"
        ),
        "country": "Sénégal",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, l'article 211 mentionne une exception pour les capitaines de navire qui se rendent coupables "
            "d'un rejet en mer d'hydrocarbures, car ils sont punis d'une peine d'emprisonnement et/ou d'amende."
        ),
        "relevant_keywords": ['dérogation', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_117",
        "axe": 7,
        "axe_label": "Sanction financière",
        "question": "Est-ce que le rejet d'hydrocarbures au Sénégal entraîne une sanction financière (amende) ?",
        "country": "Sénégal",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, selon l'article 211 du Code de l'environnement sénégalais, le rejet d'hydrocarbures en mer est "
            "puni d'une amende de cinquante millions à cinq cent millions de francs CFA."
        ),
        "relevant_keywords": ['amende', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_118",
        "axe": 8,
        "axe_label": "Sanction pénale",
        "question": "Est-ce que le rejet d'hydrocarbures au Sénégal entraîne une peine de prison ?",
        "country": "Sénégal",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, selon l'article 211 du Code de l'environnement sénégalais, le rejet d'hydrocarbures en mer est "
            "puni d'un emprisonnement allant de un (01) an à cinq (05) ans et d'une amende allant de cinquante "
            "millions (50.000.000) à cinq cent millions (500.000.000) de francs CFA ou de l'une de ces deux "
            "peines."
        ),
        "relevant_keywords": ['emprisonnement', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_119",
        "axe": 9,
        "axe_label": "Contrôle — acteurs institutionnels",
        "question": (
            "Est-ce que au Sénégal, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction du rejet d'hydrocarbures ?"
        ),
        "country": "Sénégal",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, les agents assermentés du Ministère en charge de l'Environnement et du Ministère en charge des "
            "Hydrocarbures sont désignés pour assurer le contrôle et le suivi environnemental des opérations "
            "pétrolières (Art. 130)."
        ),
        "relevant_keywords": ['administration', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_120",
        "axe": 10,
        "axe_label": "Contrôle — temporalité",
        "question": (
            "Est-ce que au Sénégal, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction du rejet d'hydrocarbures ? Si ces procédures existent, vérifiez "
            "si elles précisent des périodes (temporalité) spécifiques pour le contrôle du respect de "
            "l'interdiction du rejet d'hydrocarbures."
        ),
        "country": "Sénégal",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, les agents assermentés du Ministère en charge de l'Environnement et du Ministère en charge des "
            "Hydrocarbures sont désignés pour assurer le contrôle et le suivi environnemental des opérations "
            "pétrolières (Art. 130)."
        ),
        "relevant_keywords": ['période', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_121",
        "axe": 11,
        "axe_label": "Contrôle — zones",
        "question": (
            "Est-ce que au Sénégal, des procédures de contrôle sont spécifiquement décrites pour garantir ou "
            "assurer le respect de l'interdiction du rejet d'hydrocarbures ? Si ces procédures existent, vérifiez "
            "si elles précisent des lieux ou zones spécifiques pour le contrôle du respect de l'interdiction du "
            "rejet d'hydrocarbures."
        ),
        "country": "Sénégal",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, les agents assermentés du Ministère en charge de l'Environnement et du Ministère en charge des "
            "Hydrocarbures sont désignés pour assurer le contrôle et le suivi environnemental des opérations "
            "pétrolières (Art. 130)."
        ),
        "relevant_keywords": ['zone', 'hydrocarbure'],
    },

    # --- Togo ---

    {
        "id": "Q_HYD_122",
        "axe": 1,
        "axe_label": "Existence",
        "question": "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures au Togo ?",
        "country": "Togo",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, l'article 478 porte sur l'interdiction du rejet d'hydrocarbures dans les eaux maritimes, avec "
            "certaines exceptions."
        ),
        "relevant_keywords": ['interdit', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_123",
        "axe": 2,
        "axe_label": "Zonage",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures au Togo qui "
            "précise que cette mesure n'est applicable qu'à certaines zones, aires ou régions ?"
        ),
        "country": "Togo",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, l'article 471 spécifie que les dispositions des articles 477 et 478 ne s'appliquent pas dans la "
            "zone économique exclusive du Togo."
        ),
        "relevant_keywords": ['zone', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_124",
        "axe": 3,
        "axe_label": "Temporalité",
        "question": (
            "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures au Togo qui "
            "précise que cette mesure n'est pas applicable en permanence (temporalité) ?"
        ),
        "country": "Togo",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Non, il n'y a pas d'article dans le contexte qui stipule une exception permanente à l'interdiction "
            "du rejet d'hydrocarbures au Togo."
        ),
        "relevant_keywords": ['période', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_125",
        "axe": 4,
        "axe_label": "Types d\'activités concernées",
        "question": (
            "Est-ce que le texte juridique précise les types d'activités concernées par l'interdiction du rejet "
            "d'hydrocarbures au Togo ?"
        ),
        "country": "Togo",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, le texte juridique précise que l'interdiction de rejet d'hydrocarbures s'applique aux navires "
            "non pétroliers (Art. 477)."
        ),
        "relevant_keywords": ['navire', 'rejet'],
    },

    {
        "id": "Q_HYD_126",
        "axe": 5,
        "axe_label": "Exceptions hors santé/ordre/recherche",
        "question": (
            "Est-ce que le texte juridique mentionne des exceptions à l'interdiction du rejet d'hydrocarbures au "
            "Togo ? Vérifie si ce texte inclut des exceptions relatives à d'autres domaines que de la santé, de "
            "l'ordre public et de la recherche."
        ),
        "country": "Togo",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, le texte juridique mentionne des exceptions à l'interdiction du rejet d'hydrocarbures au Togo. "
            "Selon l'article 477, les navires non pétroliers peuvent rejeter des hydrocarbures à la mer si "
            "certaines conditions sont réunies, notamment si le navire est en navigation hors des eaux "
            "territoriales et utilise un dispositif de surveillance continue et de contrôle des rejets "
            "d'hydrocarbures."
        ),
        "relevant_keywords": [],
        "is_piege": True,
    },

    {
        "id": "Q_HYD_127",
        "axe": 6,
        "axe_label": "Exceptions / dérogations spécifiques",
        "question": (
            "Est-ce que le texte juridique mentionne des exceptions à l'interdiction du rejet d'hydrocarbures au "
            "Togo ?"
        ),
        "country": "Togo",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, l'article 477 mentionne des exceptions à l'interdiction du rejet d'hydrocarbures dans les eaux "
            "maritimes au Togo."
        ),
        "relevant_keywords": ['dérogation', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_128",
        "axe": 7,
        "axe_label": "Sanction financière",
        "question": "Est-ce que le rejet d'hydrocarbures au Togo entraîne une sanction financière (amende) ?",
        "country": "Togo",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Non, il n'y a pas de mention explicite d'une amende pour les rejets d'hydrocarbures dans les "
            "articles fournis."
        ),
        "relevant_keywords": ['amende', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_129",
        "axe": 8,
        "axe_label": "Sanction pénale",
        "question": "Est-ce que le rejet d'hydrocarbures au Togo entraîne une peine de prison ?",
        "country": "Togo",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Non, l'article juridique ne mentionne pas de peine de prison pour les dommages dus à la pollution "
            "par les hydrocarbures."
        ),
        "relevant_keywords": ['emprisonnement', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_130",
        "axe": 9,
        "axe_label": "Contrôle — acteurs institutionnels",
        "question": (
            "Est-ce que au Togo, des procédures de contrôle sont spécifiquement décrites pour garantir ou assurer "
            "le respect de l'interdiction du rejet d'hydrocarbures ?"
        ),
        "country": "Togo",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, au Togo, les procédures de contrôle sont spécifiquement décrites dans l'article 503 de la loi "
            "n°2016-028 portant code de la marine marchande. Le contrôle technique des dispositifs de prévention "
            "de la pollution à bord des navires est effectué par l'administration maritime, conformément aux "
            "Annexes I, II, IV, V et VII de la convention MARPOL 73/78. Les contrôles sont effectués à bord des "
            "navires étrangers dans les eaux et ports togolais, en tenant compte des dispositions de l'article 5 "
            "de la convention MARPOL 73/78."
        ),
        "relevant_keywords": ['administration', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_131",
        "axe": 10,
        "axe_label": "Contrôle — temporalité",
        "question": (
            "Est-ce que au Togo, des procédures de contrôle sont spécifiquement décrites pour garantir ou assurer "
            "le respect de l'interdiction du rejet d'hydrocarbures ? Si ces procédures existent, vérifiez si "
            "elles précisent des périodes (temporalité) spécifiques pour le contrôle du respect de l'interdiction "
            "du rejet d'hydrocarbures."
        ),
        "country": "Togo",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, au Togo, les procédures de contrôle sont spécifiquement décrites dans l'article 503 de la loi "
            "n°2016-028 portant code de la marine marchande. Le contrôle technique des dispositifs de prévention "
            "de la pollution à bord des navires est effectué par l'administration maritime, conformément aux "
            "Annexes I, II, IV, V et VII de la convention MARPOL 73/78. Les contrôles sont effectués à bord des "
            "navires étrangers dans les eaux et ports togolais, en tenant compte des dispositions de l'article 5 "
            "de la convention MARPOL 73/78."
        ),
        "relevant_keywords": ['période', 'hydrocarbure'],
    },

    {
        "id": "Q_HYD_132",
        "axe": 11,
        "axe_label": "Contrôle — zones",
        "question": (
            "Est-ce que au Togo, des procédures de contrôle sont spécifiquement décrites pour garantir ou assurer "
            "le respect de l'interdiction du rejet d'hydrocarbures ? Si ces procédures existent, vérifiez si "
            "elles précisent des lieux ou zones spécifiques pour le contrôle du respect de l'interdiction du "
            "rejet d'hydrocarbures."
        ),
        "country": "Togo",
        "theme": "rejets_hydrocarbures",
        "ground_truth": (
            "Oui, au Togo, les procédures de contrôle sont spécifiquement décrites dans l'article 503 de la loi "
            "n°2016-028 portant code de la marine marchande. Le contrôle technique des dispositifs de prévention "
            "de la pollution à bord des navires est effectué par l'administration maritime togolaise, "
            "conformément aux Annexes I, II, IV, V et VII de la convention MARPOL 73/78. Les contrôles sont "
            "effectués dans les eaux et ports togolais, en tenant compte des dispositions de l'article 5 de la "
            "convention MARPOL 73/78."
        ),
        "relevant_keywords": ['zone', 'hydrocarbure'],
    },

]

# =============================================================================
# BENCHMARK_QUERIES_EVAL — Sous-ensemble stratifié pour l'évaluation RAGAS
# =============================================================================
#
# Stratégie : 1 question par (thème × axe × groupe de pays)
#
#   Groupe A — corpus riche  : Bénin, Cameroun, Sénégal, Gabon
#   Groupe B — corpus moyen  : Maroc, Tunisie, Congo, Guinée
#   Groupe C — corpus léger  : Comores, Djibouti, Madagascar, Côte d'Ivoire,
#                               Togo, Mauritanie
#
# Résultat attendu : ~66 questions (vs 263) — 2 thèmes × 11 axes × 3 groupes
# Seed fixe (42) pour garantir la reproductibilité.
# Les questions pièges sont exclues sauf si le bucket n'en contient que.
#
# Usage dans generate_ragas_data.py :
#   from benchmark_queries import BENCHMARK_QUERIES_EVAL
#   ...
#   queries = list(BENCHMARK_QUERIES_EVAL)
# =============================================================================

import random as _random
from collections import defaultdict as _defaultdict

_GROUPES_PAYS = {
    "A": ["Bénin", "Cameroun", "Sénégal", "Gabon"],
    "B": ["Maroc", "Tunisie", "Congo", "Guinée"],
    "C": ["Comores", "Djibouti", "Madagascar", "Côte d'Ivoire", "Togo", "Mauritanie"],
}
_PAYS_GROUPE = {p: g for g, pays in _GROUPES_PAYS.items() for p in pays}


def _sample_eval_queries(queries, seed: int = 42):
    """
    Échantillonnage stratifié : 1 question par (thème × axe × groupe_pays).
    Préfère les non-pièges ; prend un piège uniquement si le bucket n'en
    contient pas d'autre.
    """
    rng = _random.Random(seed)
    buckets = _defaultdict(list)
    for q in queries:
        groupe = _PAYS_GROUPE.get(q.get("country"), "C")
        key = (q.get("theme"), q.get("axe"), groupe)
        buckets[key].append(q)

    selected = []
    for key in sorted(buckets):
        items = buckets[key]
        non_pieges = [q for q in items if not q.get("is_piege")]
        pool = non_pieges if non_pieges else items
        selected.append(rng.choice(pool))
    return selected


BENCHMARK_QUERIES_EVAL = _sample_eval_queries(BENCHMARK_QUERIES)
