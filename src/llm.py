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

from . import config, foundry
from .retrieval import RetrievedChunk, get_top_chunks

# Sistem istemi: modelin davranisini belirleyen en kritik parca.
SYSTEM_PROMPT = (
    "Sen, yalnizca sana verilen BAGLAM'a dayanarak soru cevaplayan bir "
    "yardimci asistansin. Kurallar:\n"
    "1. Cevabini SADECE asagidaki baglamdaki bilgilere dayandir. "
    "Kendi genel bilgini kullanma.\n"
    "2. Eger cevap baglamda yoksa, tahmin yurutme; acikca "
    "'Bu konuda dokumanlarimda bilgi bulunmuyor.' de.\n"
    "3. Cevabin sonunda, kullandigin bilgilerin kaynak dosya adini "
    "'Kaynak: <dosya>' seklinde belirt.\n"
    "4. Kisa, net ve Turkce cevap ver."
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
    user_content = (
        f"BAGLAM:\n{context}\n\n"
        f"SORU: {question}\n\n"
        "Yukaridaki baglama dayanarak soruyu cevapla."
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
    answer = response.choices[0].message.content

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
