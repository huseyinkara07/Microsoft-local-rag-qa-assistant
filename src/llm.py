"""
llm.py - Layer 5: LLM entegrasyonu + prompt tasarimi
====================================================

RAG'in "Generate" adimi. Retrieval'dan gelen chunk'lari baglam olarak alip
Foundry Local chat modeline verir ve kaynak-temelli bir cevap uretir.

Prompt tasariminin cekirdegi (halusinasyonu onlemek icin):
    - Modele "YALNIZCA verilen baglami kullan" talimati verilir.
    - Cevap baglamda yoksa "bilmiyorum" demesi istenir (uydurma yasak).
    - Kaynak dosya adlari baglama eklenir, boylece model kaynak gosterebilir.

Tasarim notu: prompt kurma mantigi (build_context / build_messages) saf
fonksiyonlardir; SDK olmadan test edilebilir. Sadece answer_query() modele
gercekten baglanir.
"""

from __future__ import annotations

import re

from . import config, foundry
from .retrieval import RetrievedChunk, get_top_chunks

# Sistem istemi: modelin davranisini belirleyen en kritik parca.
# Not: Kucuk modellerin talimatlari cevaba "papagan gibi" kopyalamasini
# onlemek icin talimatlar numarali liste yerine kisa duz metin olarak verilir
# ve en sonda "sadece cevabi yaz" denir.
SYSTEM_PROMPT = (
    "Sen KampusAsistan'sin; universite ogrencilerine yonetmelik ve kampus "
    "konularinda yardimci olan bir asistansin. Yalnizca sana verilen BAGLAM'daki "
    "bilgilere dayanarak kisa, net ve anlasilir Turkce cevap ver. Baglamda cevap "
    "yoksa sadece 'Bu konuda elimde bilgi yok.' de; asla tahmin etme veya baglam "
    "disi bilgi ekleme. Cevabinin sonunda kullandigin kaynagi '(Kaynak: dosya)' "
    "biciminde belirt. Talimatlari tekrarlama, sadece cevabi yaz."
)

# Modelden alinan chat client'i onbelleklenir (tekrar yukleme olmasin).
_chat_client = None


def _get_chat_client():
    """Chat client'ini (gerekirse modeli yukleyerek) dondurur."""
    global _chat_client
    if _chat_client is None:
        model = foundry.load_model(config.CHAT_MODEL)
        _chat_client = model.get_chat_client()
    return _chat_client


def strip_thinking(text: str) -> str:
    """Modelin 'dusunme' (<think>...</think>) blogunu cevaptan temizler.

    qwen3 gibi modeller cevaptan once muhakemelerini <think> etiketleri arasinda
    yazabilir. Bu blok kullaniciya gosterilmemeli. /no_think talimatina ragmen
    gelirse diye kod tarafinda da temizliyoruz (garanti).
    """
    # Kapanis etiketi varsa, sonrasindaki asil cevabi al.
    if "</think>" in text:
        text = text.split("</think>")[-1]
    # Artakalan etiketleri/bloklari temizle.
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    text = text.replace("<think>", "").replace("</think>", "")
    return text.strip()


def build_context(chunks: list[RetrievedChunk]) -> str:
    """Retrieval sonuclarini, kaynak etiketli tek bir baglam metnine cevirir.

    Her chunk '[Kaynak: dosya]' basligiyla ayrilir; boylece model hangi
    bilginin nereden geldigini gorup kaynak gosterebilir.
    """
    parts = []
    for chunk in chunks:
        parts.append(f"[Kaynak: {chunk.source}]\n{chunk.content}")
    return "\n\n---\n\n".join(parts)


def build_messages(question: str, chunks: list[RetrievedChunk]) -> list[dict]:
    """Chat API'sine gonderilecek system + user mesajlarini kurar."""
    context = build_context(chunks)
    # "/no_think": qwen3 gibi 'dusunen' modellerde muhakeme (reasoning) modunu
    # kapatir; boylece dogrudan cevap uretilir (daha hizli ve temiz cikti).
    user_content = (
        f"BAGLAM:\n{context}\n\n"
        f"SORU: {question}\n\n"
        "Yukaridaki baglama dayanarak soruyu cevapla. /no_think"
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]


def answer_query(
    question: str, k: int = config.TOP_K
) -> tuple[str, list[RetrievedChunk]]:
    """Bir soruyu uctan uca cevaplar: retrieve -> augment -> generate.

    Returns:
        (cevap_metni, kullanilan_chunk_listesi)
        Chunk listesi CLI'da kaynaklari gostermek/debug icin de dondurulur.
    """
    # 1. Retrieve: en alakali chunk'lari bul
    chunks = get_top_chunks(question, k)
    if not chunks:
        return (
            "Bilgi tabaninda dokuman bulunamadi. Once 'python -m src.build_index' "
            "ile indeksleme yapin.",
            [],
        )

    # 2. Augment: baglami prompt'a yerlestir
    messages = build_messages(question, chunks)

    # 3. Generate: chat modelinden cevap al
    client = _get_chat_client()
    response = client.complete_chat(messages)
    answer = strip_thinking(response.choices[0].message.content)

    return answer, chunks


if __name__ == "__main__":
    # Standalone test: python -m src.llm "sorunuz"
    import sys

    question = sys.argv[1] if len(sys.argv) > 1 else "Foundry Local nedir?"
    print(f"Soru: {question}\n")

    answer, used_chunks = answer_query(question)
    print("Cevap:")
    print(answer)
    print("\n--- Kullanilan kaynaklar ---")
    for c in used_chunks:
        print(f"  {c.source} (skor={c.score:.4f})")
