"""
retrieval.py - Layer 4: Query embed -> cosine similarity -> top-K
=================================================================

Kullanicinin sorusuna en alakali chunk'lari bulur:
    1. Soruyu ayni embedding modeliyle vektore cevir.
    2. SQLite'taki tum chunk vektorleriyle cosine similarity hesapla.
    3. En yuksek skorlu top-K chunk'i baglam olarak dondur.

Kucuk veri kumemiz icin tum vektorleri bellege okuyup brute-force benzerlik
hesaplamak yeterlidir (resmi planin onerdigi yaklasim). Cok buyuk N icin
ozel bir vektor veritabani gerekirdi.

Tasarim notu: asil siralama mantigi rank_chunks() icinde ayristirildi.
Boylece bu fonksiyon Foundry Local olmadan, sahte vektorlerle test edilebilir.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from . import config, database, embeddings


@dataclass
class RetrievedChunk:
    """Retrieval sonucu: bir chunk ve sorguya benzerlik skoru."""
    source: str    # Kaynak dosya adi (cevapta kaynak gostermek icin)
    content: str   # Chunk metni (LLM'e baglam olarak verilecek)
    score: float   # Cosine similarity (-1..1; yuksek = daha alakali)


def _cosine_similarities(query_vec: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """query_vec (d,) ile matrix'in (n, d) her satiri arasinda cosine similarity.

    Cosine similarity = normalize edilmis vektorlerin nokta carpimi.
    1e-10 eklentisi sifir vektorde bolme hatasini onler.
    """
    q_norm = query_vec / (np.linalg.norm(query_vec) + 1e-10)
    row_norms = np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-10
    matrix_norm = matrix / row_norms
    return matrix_norm @ q_norm  # (n,) skor vektoru


def rank_chunks(
    query_vector: list[float],
    chunks: list[tuple[int, str, str, list[float]]],
    k: int = config.TOP_K,
) -> list[RetrievedChunk]:
    """Verilen sorgu vektorune gore chunk'lari siralar, en iyi k tanesini dondurur.

    chunks: database.fetch_all_chunks() ciktisi (id, source, content, embedding).
    """
    if not chunks:
        return []

    matrix = np.array([emb for (_id, _src, _content, emb) in chunks], dtype=float)
    query = np.array(query_vector, dtype=float)

    scores = _cosine_similarities(query, matrix)

    # Skorlari azalan sirada sirala, ilk k tanesini al
    top_indices = np.argsort(scores)[::-1][:k]

    results: list[RetrievedChunk] = []
    for i in top_indices:
        _id, source, content, _emb = chunks[int(i)]
        results.append(
            RetrievedChunk(source=source, content=content, score=float(scores[i]))
        )
    return results


def get_top_chunks(query: str, k: int = config.TOP_K) -> list[RetrievedChunk]:
    """Bir soru icin en alakali k chunk'i SQLite'tan bulup dondurur.

    Uctan uca: soruyu embed et -> DB'den tum chunk'lari oku -> siralayip dondur.
    """
    query_vector = embeddings.embed_text(query)

    conn = database.get_connection()
    chunks = database.fetch_all_chunks(conn)
    conn.close()

    return rank_chunks(query_vector, chunks, k)


if __name__ == "__main__":
    # Standalone test: python -m src.retrieval "sorunuz"
    import sys

    query = sys.argv[1] if len(sys.argv) > 1 else "Foundry Local nedir?"
    print(f"Soru: {query}\n")

    results = get_top_chunks(query)
    if not results:
        print("Sonuc yok. Once 'python -m src.build_index' ile indeksleme yapin.")
    for rank, r in enumerate(results, start=1):
        preview = r.content[:150].replace("\n", " ")
        print(f"#{rank} [skor={r.score:.4f}] ({r.source})")
        print(f"    {preview}...\n")
