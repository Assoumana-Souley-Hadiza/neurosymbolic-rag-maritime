import sys
from pathlib import Path

# Ajouter le dossier racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag.ingestion.pdf_extractor import PDFExtractor
from rag.config import CHUNKS_DIR
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    print("\n" + "="*60)
    print("  [START] TEST D'EXTRACTION PDF (SANS EMBEDDING)")
    print("="*60 + "\n")

    extractor = PDFExtractor()
    
    print("Extraction des documents en cours... (ça peut prendre quelques minutes)\n")
    chunks, stats = extractor.process_all_pdfs()
    
    if chunks:
        # On sauvegarde les chunks pour que vous puissiez les vérifier
        output_file = "all_chunks_TEST.json"
        extractor.save_chunks(chunks, output_file=output_file)
        
        print("\n" + "="*60)
        print("  [SUCCÈS] EXTRACTION TERMINÉE")
        print("="*60)
        print(f"Total PDFs traités : {stats['successful']} / {stats['total_pdfs']}")
        print(f"Total chunks générés : {stats['total_chunks']}")
        print(f"\nNote : Les {stats['failed']} documents non traités sont soit des doublons (déjà vus), soit des PDFs images.")
        print(f"\n[INFO] Vérifiez le fichier : {CHUNKS_DIR / output_file}")
    else:
        print("\n[ERREUR] Aucun chunk généré. Vérifiez les logs.")

if __name__ == "__main__":
    main()
