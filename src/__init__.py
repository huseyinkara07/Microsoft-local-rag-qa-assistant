"""src - Local RAG Q&A Assistant cekirdek modulleri.

Her katman kendi modulunde yasar:
    ingestion.py   - dokuman okuma + chunking          (Layer 2)
    database.py    - SQLite schema + I/O               (Layer 3)
    embeddings.py  - Foundry Local embedding uretimi   (Layer 3)
    retrieval.py   - cosine similarity + top-K         (Layer 4)
    llm.py         - chat modeli + prompt tasarimi      (Layer 5)
    cli.py         - soru-cevap dongusu                 (Layer 6)
"""
