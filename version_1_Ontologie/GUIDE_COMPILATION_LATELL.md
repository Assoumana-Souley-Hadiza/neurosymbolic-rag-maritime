# Guide de Compilation - Article LaTeLL 2026

## 📄 Fichiers créés

- **`article_latell2026.tex`** — Article principal suivant le template LaTeLL 2026
- **`maritime-rag.bib`** — Fichier de références bibliographiques

## 🔧 Prérequis

Pour compiler l'article, vous avez besoin de:
- **TeX/LaTeX** (MiKTeX sur Windows, TeX Live sur Linux/Mac)
- **pdflatex** — Compilateur PDF
- **bibtex** — Gestionnaire de bibliographie

### Installation rapide

#### Windows (MiKTeX)
```powershell
# Télécharger depuis https://miktex.org/download
# Installer avec l'assistant graphique
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get install texlive-latex-full texlive-fonts-recommended
```

#### macOS (Homebrew)
```bash
brew install mactex
```

## 📝 Compilation

### Depuis le terminal PowerShell (Windows)

```powershell
cd c:\Users\HP\Desktop\stage_RAG\version_1_Ontologie

# 1. Compilation initiale
pdflatex -interaction=nonstopmode article_latell2026.tex

# 2. Traitement de la bibliographie
bibtex article_latell2026

# 3. Deuxième compilation (pour références)
pdflatex -interaction=nonstopmode article_latell2026.tex

# 4. Troisième compilation (pour table des matières et index)
pdflatex -interaction=nonstopmode article_latell2026.tex
```

### Depuis VS Code

**Option 1: Extension LaTeX Workshop**
- Installer l'extension "LaTeX Workshop" (James Yu)
- Ouvrir `article_latell2026.tex`
- Clic droit → "Build LaTeX project"

**Option 2: Makefile (Linux/Mac)**
```bash
make all
```

## 🎯 Résultat attendu

Après compilation, vous obtiendrez:
- **`article_latell2026.pdf`** — Votre article au format PDF

### Fichiers générés (à ignorer)
```
article_latell2026.aux
article_latell2026.log
article_latell2026.blg
article_latell2026.bbl
article_latell2026.out
```

## ✅ Vérification

Après compilation, vérifiez:
1. ✓ Le PDF s'ouvre correctement
2. ✓ Les références sont bien numérotées
3. ✓ La table des matières est complète
4. ✓ Les figures et tableaux s'affichent

## 🔍 Troubleshooting

### Erreur: "! Undefined control sequence"
**Solution**: Assurez-vous que le package `latell` est correctement placé dans le même répertoire.

### Erreur: "Bibliography not found"
**Solution**: Vérifiez que `maritime-rag.bib` est dans le même répertoire et relancez `bibtex`.

### Références manquantes
**Solution**: Relancez les 4 commandes de compilation dans l'ordre exact.

### Fichier trop gros
**Solution**: Supprimez les fichiers `.aux`, `.log`, etc. et recommencez.

## 📊 Structure de l'article

L'article contient:

### Sections principales
1. **Abstract** — Résumé (200 mots)
2. **Introduction** — Contexte et contributions
3. **Related Work** — État de l'art
4. **System Architecture** — Description technique détaillée (5 phases)
5. **Implementation Details** — Aspects pratiques
6. **Experimental Setup** — Méthodologie
7. **Results** — Tableaux de résultats
8. **Discussion** — Interprétation
9. **Future Work** — Perspectives
10. **Conclusion** — Synthèse
11. **References** — Bibliographie

### Contenus fidèles au projet
- ✅ 58 documents PDF (159 MB)
- ✅ 1,250+ articles juridiques
- ✅ 8 interdictions maritimes
- ✅ 3 retrievers (dense, sparse, graph)
- ✅ Architecture à 5 phases
- ✅ Multilingual (FR/EN)
- ✅ ChromaDB + BM25 + Neo4j
- ✅ Métriques de performance mesurées

## 🎓 Pour soumettre à LaTeLL 2026

### Avant soumission

1. **Décommenter la ligne `\aclfinalcopy`** (pour version finale uniquement)
2. **Ajouter le Paper ID**: Remplacer `***` par votre ID
3. **Compléter les auteurs**: Ajouter noms réels et affiliations
4. **Vérifier la longueur**: Max 8 pages (plus références illimitées)
5. **Relire**: Orthographe, grammaire, formules

### Ligne de commande LaTeX pour soumettre
```bash
# Créer une version anonymisée
pdflatex -interaction=nonstopmode article_latell2026.tex
bibtex article_latell2026
pdflatex -interaction=nonstopmode article_latell2026.tex
pdflatex -interaction=nonstopmode article_latell2026.tex

# Le PDF est prêt: article_latell2026.pdf
```

## 📋 Checklist

- [ ] TeX/LaTeX installé
- [ ] Fichiers `.tex` et `.bib` dans le même répertoire
- [ ] Compilation réussie (4 passes)
- [ ] PDF généré sans erreurs
- [ ] Références bibliographiques valides
- [ ] Format A4 vérifié
- [ ] Marges correctes (2.5 cm partout)
- [ ] Police Times Roman appliquée

## 🔗 Ressources utiles

- **Overleaf**: https://www.overleaf.com/ (compilateur en ligne)
- **LaTeLL 2026 Templates**: https://latell.org/2026/latell2026/latell2026-templates.zip
- **LKIF-Core**: http://www.estrellaproject.org/ (ontologie juridique)

## 💡 Conseils

- Utilisez Overleaf pour collaborer facilement
- Testez compilation avant modification majeure
- Gardez sauvegardes des fichiers `.tex`
- Versionnez avec Git si possible
