"""
build_index.py - Layer 3 pipeline: dokumanlari indeksle
=======================================================

Uctan uca indeksleme:
    1. Dokumanlari chunk'la      (Layer 2: ingestion)
    2. Her chunk'i embed et       (embeddings)
    3. SQLite'a yaz                (database)

Calistirma:
    python -m src.build_index

Bu betik "re-index" mantigiyla calisir: onceki chunk'lari silip yeniden
yazar. Yani dokuman ekleyip/degistirdiginde tekrar calistirman yeterli.
"""

from __future__ import annotations

from . import database, embeddings
from .ingestion import ingest


def build_index() -> int:
    """Dokumanlari indeksler ve yazilan chunk sayisini dondurur."""
    # 1. Chunk'la
    chunks = ingest()
    if not chunks:
        print("Uyari: data/documents/ icinde islenecek dokuman bulunamadi.")
        return 0
    print(f"{len(chunks)} chunk uretildi. Embedding'ler hesaplaniyor...")

    # 2. Embed et (batch - tek seferde)
    vectors = embeddings.embed_texts([c.content for c in chunks])

    # 3. SQLite'a yaz (once temizle -> yeniden indeksle)
    records = [
        (chunk.source, chunk.content, vector)
        for chunk, vector in zip(chunks, vectors)
    ]
    conn = database.get_connection()
    database.clear_chunks(conn)
    written = database.insert_chunks(conn, records)

    # Dogrulama: DB'deki kayit sayisi
    total = database.count_chunks(conn)
    conn.close()

    print(f"Tamamlandi: {written} chunk SQLite'a yazildi (DB toplami: {total}).")
    if vectors:
        print(f"Embedding boyutu: {len(vectors[0])}")
    return written


if __name__ == "__main__":
    build_index()
