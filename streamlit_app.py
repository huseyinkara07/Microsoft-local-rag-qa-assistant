"""
streamlit_app.py - KampusAsistan web arayuzu (plan Option B)
============================================================

CLI ile ayni backend'i (src.llm.answer_query) kullanan, sohbet tarzi bir web
arayuzu. Universite ogrencilerine yonelik "KampusAsistan": yonetmelik ve kampus
sorularini yerel dokumanlara dayanarak, kaynak gostererek yanitlar.

Calistirma:
    streamlit run streamlit_app.py

Not: Backend mantigi degismez; bu dosya yalnizca bir sunum katmanidir.
"""

from __future__ import annotations

import streamlit as st

from src import config, database
from src.build_index import build_index
from src.llm import answer_query

APP_NAME = "KampüsAsistan"
APP_TAGLINE = "Üniversite yönetmelik ve kampüs sorularınıza çevrimdışı, kaynak-temelli yanıtlar"

# Ornek sorular (kullanici sohbete baslamadan gosterilir)
EXAMPLE_QUESTIONS = [
    "Bütünleme sınavına kimler girebilir?",
    "Zorunlu staj kaç iş günü?",
    "Devamsızlık sınırı nedir?",
    "Başarı bursu için gereken ortalama nedir?",
]


# --- Yardimci fonksiyonlar ---

def _index_size() -> int:
    """Bilgi tabanindaki chunk sayisi (0 = bos)."""
    conn = database.get_connection()
    try:
        return database.count_chunks(conn)
    finally:
        conn.close()


@st.cache_resource(show_spinner="Model yükleniyor (ilk seferde indirilebilir)...")
def _warmup() -> bool:
    """Chat + embedding modellerini bir kez yukler (tekrar yukleme olmasin)."""
    answer_query("merhaba")
    return True


def _answer_and_store(question: str) -> None:
    """Bir soruyu isler ve hem soruyu hem cevabi sohbet gecmisine ekler."""
    st.session_state.messages.append({"role": "user", "content": question})
    _warmup()
    answer, chunks = answer_query(question)
    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "sources": chunks}
    )


# --- Sayfa yapilandirmasi + stil ---

st.set_page_config(page_title=APP_NAME, page_icon="🎓", layout="centered")

st.markdown(
    """
    <style>
      /* Ust baslik (hero) karti */
      .hero {
        background: linear-gradient(135deg, #0F6CBD 0%, #2B88D8 100%);
        padding: 1.6rem 1.8rem; border-radius: 16px; margin-bottom: 1.2rem;
        color: #ffffff; box-shadow: 0 6px 20px rgba(15,108,189,0.25);
      }
      .hero h1 { color: #fff; margin: 0; font-size: 1.9rem; }
      .hero p  { color: #eaf3fb; margin: .4rem 0 0; font-size: .98rem; }
      /* Ornek soru butonlarini yumusat */
      div[data-testid="stButton"] > button {
        border-radius: 10px; border: 1px solid #d7e3f2; text-align: left;
        background: #F3F6FB; font-weight: 500;
      }
      div[data-testid="stButton"] > button:hover {
        border-color: #0F6CBD; color: #0F6CBD;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="hero">
      <h1>🎓 {APP_NAME}</h1>
      <p>{APP_TAGLINE}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Kenar cubugu ---

with st.sidebar:
    st.header("ℹ️ Hakkında")
    st.write(
        "KampüsAsistan, sorularınızı yerel dokümanlardaki bilgilere dayanarak "
        "yanıtlar (RAG). İnternet gerektirmez; tüm modeller cihazda çalışır."
    )
    st.divider()
    st.subheader("Bilgi tabanı")
    st.metric("İndekslenmiş bölüm", _index_size())
    st.caption(f"Embedding: `{config.EMBEDDING_MODEL}`")
    st.caption(f"Chat: `{config.CHAT_MODEL}`")

    if st.button("🔄 Dokümanları yeniden indeksle", use_container_width=True):
        with st.spinner("Dokümanlar indeksleniyor..."):
            build_index()
        st.success("İndeksleme tamamlandı.")
        st.rerun()

    if st.session_state.get("messages"):
        if st.button("🗑️ Sohbeti temizle", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

# --- Sohbet durumu ---

if "messages" not in st.session_state:
    st.session_state.messages = []

# Bilgi tabani bos ise uyar ve dur
if _index_size() == 0:
    st.warning(
        "Bilgi tabanı boş. Soldaki **Dokümanları yeniden indeksle** düğmesine basın."
    )
    st.stop()

# Gecmis mesajlari goster
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🎓" if msg["role"] == "assistant" else "🧑‍🎓"):
        st.write(msg["content"])
        if msg.get("sources"):
            with st.expander("📄 Kaynaklar ve kullanılan bağlam"):
                for c in msg["sources"]:
                    st.markdown(f"**{c.source}** — benzerlik: `{c.score:.3f}`")
                    st.caption(c.content)

# Sohbet henuz bosken ornek sorulari goster
pending_question = None
if not st.session_state.messages:
    st.caption("Örnek sorularla başlayabilirsiniz:")
    cols = st.columns(2)
    for i, ex in enumerate(EXAMPLE_QUESTIONS):
        if cols[i % 2].button(ex, use_container_width=True, key=f"ex_{i}"):
            pending_question = ex

# Kullanici girisi (sayfanin altinda sabit)
typed = st.chat_input("Sorunuzu yazın...")
if typed:
    pending_question = typed

# Bir soru varsa isle ve yeniden ciz
if pending_question:
    _answer_and_store(pending_question)
    st.rerun()
