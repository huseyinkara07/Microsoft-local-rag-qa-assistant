"""
ingestion.py - Layer 2: Dokuman okuma + chunking
=================================================

Gorevi: data/documents/ klasorundeki dokumanlari (.txt, .md) okumak ve
her birini paragraf bazli, retrieval'a uygun kucuk parcalara (chunk) bolmek.

Neden chunking? RAG passage-level calisir: bir dokumanin tamamini degil,
soruyla en alakali kucuk bolumu LLM'e baglam olarak veririz. Resmi plan
~1-3 paragrafik parcalar oneriyor.

Bu katmanda EMBEDDING YOK. Sadece metin parcalari uretilir. Vektor uretimi
ve SQLite yazma Layer 3'te yapilacak.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# Proje kok dizinine gore varsayilan dokuman klasoru: <proje>/data/documents
DEFAULT_DOCS_DIR = Path(__file__).resolve().parent.parent / "data" / "documents"

# Desteklenen dosya uzantilari (duz metin tabanli)
SUPPORTED_EXTENSIONS = {".txt", ".md"}

# Chunking parametreleri
MIN_CHUNK_CHARS = 200   # Bu boyutun altindaki parcalar bir sonrakiyle birlestirilir
MAX_CHUNK_CHARS = 1000  # Bu boyutun ustundeki parcalar cumle bazli bolunur


@dataclass
class Chunk:
    """Tek bir metin parcasi ve kaynagi.

    Layer 3'te bu yapiya embedding eklenip SQLite'a yazilacak
    (schema: id, source, content, embedding).
    """
    source: str        # Kaynak dosya adi (or. "faq.md") - cevaplarda kaynak gostermek icin
    content: str       # Parcanin metni
    chunk_index: int   # Kaynak icindeki sira (0'dan baslar) - debug/izleme icin


def _split_into_paragraphs(text: str) -> list[str]:
    """Metni bos satirlara (bir veya daha fazla) gore paragraflara boler."""
    # Windows/Unix satir sonlarini normalize et
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    # Bir veya daha fazla bos satir = paragraf siniri
    raw_paragraphs = normalized.split("\n\n")
    # Her paragrafin ic bosluklarini temizle, bos olanlari at
    return [p.strip() for p in raw_paragraphs if p.strip()]


def _split_long_paragraph(paragraph: str) -> list[str]:
    """MAX_CHUNK_CHARS'i asan bir paragrafi cumle bazli daha kucuk parcalara boler."""
    if len(paragraph) <= MAX_CHUNK_CHARS:
        return [paragraph]

    # Basit cumle bolme: nokta/soru/unlem + bosluk. Kutuphane bagimliligi yok.
    import re
    sentences = re.split(r"(?<=[.!?])\s+", paragraph)

    parts: list[str] = []
    current = ""
    for sentence in sentences:
        # Cumleyi ekleyince siniri asiyorsak, mevcut parcayi kapat
        if current and len(current) + len(sentence) + 1 > MAX_CHUNK_CHARS:
            parts.append(current.strip())
            current = sentence
        else:
            current = f"{current} {sentence}".strip()
    if current.strip():
        parts.append(current.strip())
    return parts


def chunk_text(text: str) -> list[str]:
    """Bir dokumanin tam metnini chunk listesine cevirir.

    Strateji:
      1. Paragraflara bol (bos satir bazli).
      2. Cok kisa paragraflari (< MIN_CHUNK_CHARS) bir sonrakiyle birlestir
         (tek basina anlamsiz kalan basliklar/kisa satirlar icin).
      3. Cok uzun paragraflari (> MAX_CHUNK_CHARS) cumle bazli bol.
    """
    paragraphs = _split_into_paragraphs(text)

    # 2. adim: kisa paragraflari birlestir
    merged: list[str] = []
    buffer = ""
    for para in paragraphs:
        buffer = f"{buffer}\n\n{para}".strip() if buffer else para
        if len(buffer) >= MIN_CHUNK_CHARS:
            merged.append(buffer)
            buffer = ""
    if buffer:  # Artan kisa parca varsa sona ekle
        if merged:
            merged[-1] = f"{merged[-1]}\n\n{buffer}"
        else:
            merged.append(buffer)

    # 3. adim: uzun parcalari bol
    chunks: list[str] = []
    for block in merged:
        chunks.extend(_split_long_paragraph(block))

    return chunks


def ingest(docs_dir: Path | str = DEFAULT_DOCS_DIR) -> list[Chunk]:
    """Klasordeki tum desteklenen dokumanlari okuyup Chunk listesi dondurur.

    Args:
        docs_dir: Dokumanlarin bulundugu klasor (varsayilan: data/documents).

    Returns:
        Tum dokumanlardan uretilen Chunk'larin duz listesi.
    """
    docs_path = Path(docs_dir)
    if not docs_path.exists():
        raise FileNotFoundError(f"Dokuman klasoru bulunamadi: {docs_path}")

    all_chunks: list[Chunk] = []

    # Deterministik sira icin dosyalari isme gore sirala
    for file_path in sorted(docs_path.iterdir()):
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue  # .gitkeep, resimler vb. atla

        text = file_path.read_text(encoding="utf-8")
        pieces = chunk_text(text)

        for idx, piece in enumerate(pieces):
            all_chunks.append(Chunk(source=file_path.name, content=piece, chunk_index=idx))

    return all_chunks


if __name__ == "__main__":
    # Standalone test: python -m src.ingestion
    # Dokumanlari oku, ozet istatistik ve ilk birkac parcanin onizlemesini goster.
    chunks = ingest()
    print(f"Toplam {len(chunks)} chunk uretildi.\n")

    # Kaynak basina chunk sayisi
    from collections import Counter
    per_source = Counter(c.source for c in chunks)
    for source, count in per_source.items():
        print(f"  {source}: {count} chunk")

    # Ilk 3 chunk onizlemesi
    print("\n--- Ilk parcalarin onizlemesi ---")
    for c in chunks[:3]:
        preview = c.content[:120].replace("\n", " ")
        print(f"[{c.source} #{c.chunk_index}] ({len(c.content)} karakter) {preview}...")
