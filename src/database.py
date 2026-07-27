"""
database.py - Layer 3 (Bolum B): SQLite schema + I/O
====================================================

Chunk metinlerini ve embedding vektorlerini yerel bir SQLite dosyasinda saklar.
SQLite sunucusuz, tek dosyalik bir veritabanidir; yerel RAG icin idealdir.

Schema (tablo: chunks):
    id        INTEGER  - otomatik artan birincil anahtar
    source    TEXT     - kaynak dosya adi (cevaplarda kaynak gostermek icin)
    content   TEXT     - chunk metni
    embedding TEXT     - JSON-serialize edilmis float vektor

Embedding'i neden TEXT (JSON) olarak sakliyoruz? Resmi plan blob veya
JSON metin onerir. JSON okunabilir ve tasinabilir; kucuk veri kumemizde
performans sorunu yaratmaz. Retrieval'da (Layer 4) tekrar float listesine
cevrilir.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from . import config

# Chunk + embedding satirlarini tutan tablo
_SCHEMA = """
CREATE TABLE IF NOT EXISTS chunks (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    source    TEXT NOT NULL,
    content   TEXT NOT NULL,
    embedding TEXT NOT NULL
);
"""


def get_connection(db_path: Path | str = config.DB_PATH) -> sqlite3.Connection:
    """Veritabani baglantisi acar (dosya yoksa olusturulur) ve schema'yi kurar."""
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)  # data/ klasorunu garanti et
    conn = sqlite3.connect(db_path)
    conn.execute(_SCHEMA)
    conn.commit()
    return conn


def clear_chunks(conn: sqlite3.Connection) -> None:
    """Tum chunk'lari siler. Yeniden indeksleme (re-ingest) icin kullanilir."""
    conn.execute("DELETE FROM chunks")
    conn.commit()


def insert_chunks(
    conn: sqlite3.Connection,
    records: list[tuple[str, str, list[float]]],
) -> int:
    """Coklu (source, content, embedding) kaydini tek islemde yazar.

    embedding float listesi JSON metnine cevrilerek saklanir.
    Donen deger: eklenen satir sayisi.
    """
    rows = [
        (source, content, json.dumps(embedding))
        for source, content, embedding in records
    ]
    conn.executemany(
        "INSERT INTO chunks (source, content, embedding) VALUES (?, ?, ?)",
        rows,
    )
    conn.commit()
    return len(rows)


def fetch_all_chunks(
    conn: sqlite3.Connection,
) -> list[tuple[int, str, str, list[float]]]:
    """Tum chunk'lari (id, source, content, embedding) olarak dondurur.

    embedding JSON metninden tekrar float listesine cevrilir.
    Layer 4 (retrieval) tum vektorleri bellege okuyup benzerlik hesaplar.
    """
    cursor = conn.execute("SELECT id, source, content, embedding FROM chunks")
    result: list[tuple[int, str, str, list[float]]] = []
    for row_id, source, content, embedding_json in cursor.fetchall():
        result.append((row_id, source, content, json.loads(embedding_json)))
    return result


def count_chunks(conn: sqlite3.Connection) -> int:
    """Veritabanindaki chunk sayisini dondurur (dogrulama icin)."""
    return conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
