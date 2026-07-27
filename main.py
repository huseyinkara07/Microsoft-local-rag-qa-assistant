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
Su an sadece iskelet mevcut; katmanlar tamamlandikca doldurulacaktir.
"""


def main() -> None:
    print("Local RAG Q&A Assistant - iskelet hazir (Layer 1).")
    print("Sonraki adim: dokuman ingestion (Layer 2).")


if __name__ == "__main__":
    main()
