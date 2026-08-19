"""
streamlit_app.py - Web arayuzu (plan Option B)
==============================================

CLI ile ayni backend'i (src.llm.answer_query) kullanan basit bir web arayuzu.
Kullanici tarayicida soru yazar, kaynak-temelli cevabi ve kullanilan
dokuman parcalarini gorur.

Calistirma:
    streamlit run streamlit_app.py

Not: Backend mantigi degismez; bu dosya yalnizca bir sunum katmanidir.
"""

from __future__ import annotations

import streamlit as st

from src import config, database
from src.build_index import build_index
from src.llm import answer_query


# --- Yardimci fonksiyonlar ---

def _index_size() -> int:
    """Bilgi tabanindaki chunk sayisi (0 = bos)."""
    conn = database.get_connection()
    try:
        return database.count_chunks(conn)
    finally:
        conn.close()


@st.cache_resource(show_spinner="Modeller yukleniyor (ilk seferde indirilebilir)...")
def _warmup() -> bool:
    """Chat + embedding modellerini bir kez yukler ve onbellekler.

    st.cache_resource sayesinde Streamlit her yeniden calistirmada modeli
    tekrar yuklemez; ayni surecte bir kez yuklenir.
    """
    # Kucuk bir sorgu ile embedding + chat modellerini tetikle (isinma).
    answer_query("merhaba")
    return True


# --- Sayfa ---

st.set_page_config(page_title="Local RAG Q&A Assistant", page_icon="🔎")
st.title("🔎 Local RAG Q&A Assistant")
st.caption("Foundry Local ile çevrimdışı, kaynak-temelli doküman soru-cevap")

# Kenar cubugu: bilgi tabani durumu + yeniden indeksleme
with st.sidebar:
    st.header("Bilgi tabanı")
    size = _index_size()
    st.metric("İndekslenmiş chunk", size)
    st.write(f"Dokümanlar: `{config.DOCS_DIR.name}/`")
    st.write(f"Embedding: `{config.EMBEDDING_MODEL}`")
    st.write(f"Chat: `{config.CHAT_MODEL}`")

    if st.button("🔄 Yeniden indeksle"):
        with st.spinner("Dokümanlar indeksleniyor..."):
            build_index()
        st.success("İndeksleme tamamlandı.")
        st.rerun()

# Bilgi tabani bos ise uyar
if _index_size() == 0:
    st.warning(
        "Bilgi tabanı boş. Soldaki **Yeniden indeksle** düğmesine basın "
        "veya `data/documents/` içine doküman ekleyip indeksleyin."
    )
    st.stop()

# --- Soru-cevap ---
question = st.text_input("Sorunuz", placeholder="Örn: Foundry Local hangi platformlarda çalışır?")

if question:
    _warmup()  # modeller hazir (cache'li)
    with st.spinner("Cevap üretiliyor..."):
        answer, chunks = answer_query(question)

    st.markdown("### Cevap")
    st.write(answer)

    if chunks:
        with st.expander("📄 Kullanılan kaynaklar / bağlam"):
            for c in chunks:
                st.markdown(f"**{c.source}** — benzerlik: `{c.score:.3f}`")
                st.text(c.content)
                st.divider()
