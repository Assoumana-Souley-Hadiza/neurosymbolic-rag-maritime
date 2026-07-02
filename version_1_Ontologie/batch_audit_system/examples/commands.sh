#!/bin/bash
# ============================================================
# Commandes pour lancer le système d'audit automatique
# ============================================================

# 1. DEPUIS LA RACINE - Lancer le menu interactif
python audit.py

# 2. DEPUIS LA RACINE - Test rapide
python batch_audit_system/scripts/test_quick_query.py

# 3. DEPUIS LA RACINE - Audit complet
python batch_audit_system/scripts/batch_query_system.py

# 4. DEPUIS LA RACINE - Générer questions uniquement
python batch_audit_system/scripts/batch_query_system.py --generate-only

# 5. DEPUIS LA RACINE - Interroger les questions existantes
python batch_audit_system/scripts/batch_query_system.py --query-only

# 6. DEPUIS LA RACINE - Analyser les résultats
python batch_audit_system/scripts/analyze_batch_results.py

# 7. DEPUIS LA RACINE - Générer rapport HTML
python batch_audit_system/scripts/analyze_batch_results.py --export-html

# 8. DEPUIS LA RACINE - Exporter en tous les formats
python batch_audit_system/scripts/export_batch_results.py --all

# ============================================================
# Alternative: Depuis le dossier batch_audit_system
# ============================================================

cd batch_audit_system

# Lancer le menu
python scripts/launcher_audit.py

# Test rapide
python scripts/test_quick_query.py

# Audit complet
python scripts/batch_query_system.py

# Analyser résultats
python scripts/analyze_batch_results.py

# ============================================================
# Commandes Windows (PowerShell)
# ============================================================

# Depuis la racine - Menu
python audit.py

# Audit complet
python batch_audit_system/scripts/batch_query_system.py

# Test rapide
python batch_audit_system/scripts/test_quick_query.py

# Analyser résultats
python batch_audit_system/scripts/analyze_batch_results.py

# Tous les exports
python batch_audit_system/scripts/export_batch_results.py --all

# ============================================================
# Commandes Windows (CMD)
# ============================================================

REM Lancer START_AUDIT.bat
START_AUDIT.bat

REM Ou directement
python audit.py
python batch_audit_system\scripts\batch_query_system.py
