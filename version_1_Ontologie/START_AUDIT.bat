@echo off
REM Lanceur Windows pour le système d'audit automatique
REM Exécute le menu interactif

cd /d %~dp0
python batch_audit_system/scripts/launcher_audit.py

pause
