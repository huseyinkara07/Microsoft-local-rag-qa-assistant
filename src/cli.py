"""
cli.py - Layer 6: Komut satiri arayuzu (soru-cevap dongusu)
===========================================================

Kullaniciyla etkilesimli dongu: soru yaz -> cevap al -> tekrar. Resmi planin
onerdigi "Option A: CLI" yaklasimi; backend mantigina odaklanmayi saglar.

Ozellikler:
    - Baslangicta bilgi tabani bos ise indekslemeyi teklif eder.
    - 'cikis' / 'quit' ile temiz cikis; Ctrl+C ve EOF'a da dayanikli.
    - Her cevaptan sonra kullanilan kaynaklari (dogrulama icin) listeler.
"""

from __future__ import annotations

from . import config, database
from .llm import answer_query

BANNER = (
    "=" * 60 + "\n"
    "  Local RAG Q&A Assistant  (Foundry Local, cevrimdisi)\n"
    "  Sorunuzu yazin. Cikmak icin: cikis | quit    Yardim: yardim\n"
    + "=" * 60
)

HELP_TEXT = (
    "Komutlar:\n"
    "  <soru>   - Dokumanlara dayali cevap alir\n"
    "  yardim   - Bu yardimi gosterir\n"
    "  cikis    - Programdan cikar\n"
)

# Cikis ve yardim icin kabul edilen kelimeler
_EXIT_WORDS = {"cikis", "quit", "exit", "q"}
_HELP_WORDS = {"yardim", "help", "?"}


def classify_input(text: str) -> str:
    """Kullanici girdisini siniflar: 'empty' | 'exit' | 'help' | 'question'.

    Saf fonksiyon - SDK gerektirmez, bu yuzden test edilebilir.
    """
    stripped = text.strip()
    if not stripped:
        return "empty"
    lowered = stripped.lower()
    if lowered in _EXIT_WORDS:
        return "exit"
    if lowered in _HELP_WORDS:
        return "help"
    return "question"


def _index_size() -> int:
    """Bilgi tabanindaki chunk sayisini dondurur (0 = bos)."""
    conn = database.get_connection()
    try:
        return database.count_chunks(conn)
    finally:
        conn.close()


def _print_answer(question: str) -> None:
    """Bir soruyu cevaplar ve cevabi + kaynaklari yazdirir."""
    try:
        answer, chunks = answer_query(question)
    except Exception as exc:  # Model/SDK hatalarinda dongu cokmesin
        print(f"[Hata] Cevap uretilemedi: {exc}")
        return

    print(f"\n{answer}\n")
    if chunks:
        # Tekrarlari onleyip kaynaklari en yuksek skoruyla goster (dogrulama icin)
        seen: dict[str, float] = {}
        for c in chunks:
            seen[c.source] = max(seen.get(c.source, 0.0), c.score)
        kaynaklar = ", ".join(f"{src} ({score:.2f})" for src, score in seen.items())
        print(f"  ↳ Kullanilan kaynaklar: {kaynaklar}")


def run() -> None:
    """Etkilesimli soru-cevap dongusunu baslatir."""
    print(BANNER)

    # Bilgi tabani bos mu? Bosza indekslemeyi teklif et.
    if _index_size() == 0:
        print(
            "\nBilgi tabani bos. data/documents/ icindeki dokumanlari "
            "indekslemek gerekiyor."
        )
        cevap = input("Simdi indekslensin mi? [E/h] ").strip().lower()
        if cevap in {"", "e", "evet", "y", "yes"}:
            from .build_index import build_index
            build_index()
        else:
            print("Indeksleme atlandi. 'python -m src.build_index' ile sonra yapabilirsiniz.")

    print("\nHazir. Sorunuzu yazin.\n")

    while True:
        try:
            user_input = input("Soru> ")
        except (EOFError, KeyboardInterrupt):
            print()  # satir sonu
            break

        kind = classify_input(user_input)
        if kind == "empty":
            continue
        if kind == "exit":
            break
        if kind == "help":
            print(HELP_TEXT)
            continue

        _print_answer(user_input.strip())

    print("Gorusuruz!")


if __name__ == "__main__":
    run()
