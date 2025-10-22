"""
Mastercam Türkçe Dokümantasyon Asistanı
Streamlit Web Arayüzü
"""

import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv
import sys

# Modülleri import et
sys.path.append(str(Path(__file__).parent))
from src.gemini_assistant import MastercamAssistant
from utils.vector_db import VectorDatabase

# Sayfa yapılandırması
st.set_page_config(
    page_title="Mastercam Türkçe Asistan",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS stilleri
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        padding: 1rem 0;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #E3F2FD;
        border-left: 4px solid #1E88E5;
    }
    .assistant-message {
        background-color: #F5F5F5;
        border-left: 4px solid #43A047;
    }
    .source-box {
        background-color: #FFF9C4;
        padding: 0.5rem;
        border-radius: 0.3rem;
        margin-top: 0.5rem;
        font-size: 0.9rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1E88E5;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_assistant():
    """Asistanı başlatır (sadece bir kez)"""
    # .env dosyasını yükle
    load_dotenv()

    # API key kontrolü
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("⚠️ GEMINI_API_KEY bulunamadı! Lütfen .env dosyasını oluşturun.")
        st.stop()

    # Path'leri otomatik bul
    app_dir = Path(__file__).parent  # mastercam_assistant/
    project_root = app_dir.parent  # D:\MASTERCAM2025\
    db_path = app_dir / "data" / "chromadb"
    docs_path = project_root / "tr"

    # Debug bilgisi
    print(f"DEBUG: app_dir = {app_dir}")
    print(f"DEBUG: db_path = {db_path}")
    print(f"DEBUG: db_path exists? {db_path.exists()}")
    if db_path.exists():
        print(f"DEBUG: db_path contents: {list(db_path.glob('*'))}")

    # Vector DB yükle
    db = VectorDatabase(persist_directory=str(db_path))
    if not db.get_collection():
        st.error(f"⚠️ Vector database yüklenmedi!")
        st.info(f"📂 Aranan klasör: {db_path}")
        st.info(f"📁 Klasör var mı? {db_path.exists()}")
        st.warning("Terminalde şu komutu çalıştırın: `python scripts/setup_database.py`")
        st.stop()

    # Asistan oluştur
    assistant = MastercamAssistant(api_key, db)
    return assistant, str(docs_path)


def display_message(role: str, content: str):
    """Mesajı görüntüler"""
    if role == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>👤 Siz:</strong><br>
            {content}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <strong>🤖 Asistan:</strong><br>
            {content}
        </div>
        """, unsafe_allow_html=True)


def display_sources(sources: list):
    """Kaynak dökümanları gösterir"""
    if sources:
        with st.expander("📚 Kaynak Dökümanlar", expanded=False):
            for i, source in enumerate(sources, 1):
                st.markdown(f"""
                <div class="source-box">
                    <strong>{i}. {source['title']}</strong><br>
                    📁 Kategori: {source['category']}<br>
                    📄 Dosya: {source['file_path']}
                </div>
                """, unsafe_allow_html=True)


def display_images(images: list, docs_path: str):
    """İlgili görselleri gösterir"""
    if images:
        with st.expander("🖼️ İlgili Görseller", expanded=True):
            cols = st.columns(min(len(images), 3))
            for i, img_path in enumerate(images):
                col = cols[i % 3]
                full_path = Path(docs_path) / img_path
                if full_path.exists():
                    with col:
                        st.image(str(full_path), use_container_width=True)
                        st.caption(img_path.split('/')[-1])


def main():
    """Ana uygulama"""

    # Başlık
    st.markdown('<h1 class="main-header">🔧 Mastercam Türkçe Dokümantasyon Asistanı</h1>', unsafe_allow_html=True)
    st.markdown("---")

    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/1E88E5/FFFFFF?text=Mastercam", use_container_width=True)
        st.markdown("### 📖 Hakkında")
        st.info("""
        Bu asistan, Mastercam CAD/CAM yazılımı Türkçe dokümantasyonu hakkında
        sorularınızı yanıtlar.

        **Özellikler:**
        - 🤖 Yapay zeka destekli yanıtlar
        - 🖼️ Görsel referanslar
        - 📚 Kaynak dökümanlar
        - 🇹🇷 Türkçe destek
        """)

        st.markdown("### 📊 İstatistikler")
        assistant, docs_path = initialize_assistant()
        stats = assistant.vector_db.get_stats()
        st.metric("Toplam Döküman", stats.get('total_documents', 0))

        st.markdown("---")
        if st.button("🗑️ Sohbeti Temizle"):
            st.session_state.messages = []
            assistant.clear_history()
            st.rerun()

        st.markdown("### 💡 Örnek Sorular")
        example_questions = [
            "Mastercam'de 2D çizim nasıl yapılır?",
            "CNC torna programlama adımları neler?",
            "Wireframe nasıl kullanılır?",
            "Machine simulation nedir?",
            "SOLIDWORKS dosyası nasıl içe aktarılır?"
        ]

        for question in example_questions:
            if st.button(question, key=question):
                st.session_state.messages.append({"role": "user", "content": question})
                st.rerun()

    # Sohbet geçmişini başlat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Asistanı yükle
    assistant, docs_path = initialize_assistant()

    # Sohbet geçmişini göster
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                display_message("user", message["content"])
            else:
                display_message("assistant", message["content"])

                # Kaynakları göster
                if "sources" in message:
                    display_sources(message["sources"])

                # Görselleri göster
                if "images" in message:
                    display_images(message["images"], docs_path)

    # Kullanıcı input
    st.markdown("---")
    col1, col2 = st.columns([5, 1])

    with col1:
        user_input = st.text_input(
            "Sorunuzu buraya yazın...",
            key="user_input",
            placeholder="Örn: Mastercam'de 3D modelleme nasıl yapılır?"
        )

    with col2:
        send_button = st.button("Gönder 📤", use_container_width=True)

    # Mesaj gönder
    if send_button and user_input:
        # Kullanıcı mesajını ekle
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Asistandan yanıt al
        with st.spinner("🤔 Düşünüyorum..."):
            result = assistant.chat(user_input)

            # Asistan yanıtını ekle
            st.session_state.messages.append({
                "role": "assistant",
                "content": result["response"],
                "sources": result["sources"],
                "images": result["images"]
            })

        # Sayfayı yenile
        st.rerun()


if __name__ == "__main__":
    main()
