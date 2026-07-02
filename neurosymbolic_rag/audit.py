#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wrapper - Lanceur depuis la racine du projet

Permet de lancer les scripts du système d'audit depuis n'importe où
"""

import sys
from pathlib import Path

# Naviguer vers le dossier racine
root_dir = Path(__file__).parent
audit_system_dir = root_dir / "batch_audit_system"
scripts_dir = audit_system_dir / "scripts"

# Ajouter au PYTHONPATH
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(audit_system_dir))

# Importer et lancer
if __name__ == "__main__":
    # Importer le launcher
    sys.path.insert(0, str(scripts_dir))
    from launcher_audit import main
    
    main()
