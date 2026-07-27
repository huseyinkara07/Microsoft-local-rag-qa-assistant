"""
Local RAG Q&A Assistant - Entry Point
=====================================

Offline (cihaz uzerinde) calisan, dokuman tabanli soru-cevap asistani.
Microsoft Foundry Local ile yerel embedding + chat modellerini kullanir.

Mimari (katmanlar):
    1. Proje iskeleti                <- SIMDI BURADAYIZ
    2. Dokuman ingestion + chunking  (src/ingestion.py)
    3. Embedding + SQLite yazma       (src/embeddings.py, src/database.py)
    4. Retrieval (cosine similarity)  (src/retrieval.py)
    5. LLM entegrasyonu + prompt      (src/llm.py)
    6. CLI arayuzu                    (src/cli.py)
    7. README

Bu dosya, tamamlanan katmanlari birbirine baglayan giris noktasidir.
Uygulamayi baslatir: etkilesimli soru-cevap CLI dongusu (Layer 6).

Calistirma:
    python main.py
"""

from src.cli import run


def main() -> None:
    run()


if __name__ == "__main__":
    main()
