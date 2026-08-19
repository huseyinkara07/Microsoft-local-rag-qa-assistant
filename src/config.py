"""
config.py - Merkezi proje ayarlari
==================================

Model isimleri, dosya yollari ve retrieval parametreleri tek yerde toplanir.
Katmanlar bu degerleri buradan okur; boylece bir yeri degistirmek yeter.
"""

from pathlib import Path

# --- Yollar ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "data" / "documents"   # Kaynak dokumanlar
DB_PATH = PROJECT_ROOT / "data" / "rag.db"        # SQLite veritabani (git'e girmez)

# --- Foundry Local model isimleri (katalog alias'lari) ---
APP_NAME = "local_rag_qa_assistant"
EMBEDDING_MODEL = "qwen3-embedding-0.6b"  # Retrieval icin embedding modeli
CHAT_MODEL = "qwen3-4b"                   # Cevap uretimi icin sohbet modeli (kalite dengeli, GPU'da hizli)

# --- Retrieval parametreleri ---
TOP_K = 3  # Soru basina LLM'e verilecek en alakali chunk sayisi
