"""
Gemini AI Asistan
RAG (Retrieval Augmented Generation) ile dokümantasyon soruları yanıtlar
"""

import os
import google.generativeai as genai
from typing import List, Dict, Optional
import sys
from pathlib import Path

# Utils modüllerini import et
sys.path.append(str(Path(__file__).parent.parent))
from utils.vector_db import VectorDatabase


class MastercamAssistant:
    """Mastercam Türkçe Dokümantasyon AI Asistanı"""

    def __init__(self, api_key: str, vector_db: VectorDatabase):
        """
        Args:
            api_key: Google Gemini API anahtarı
            vector_db: VectorDatabase instance
        """
        # Gemini API yapılandırması
        genai.configure(api_key=api_key)

        # Gemini model (Türkçe için en uygun)
        # Not: Model ismi API versiyonuna göre değişebilir
        try:
            self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
        except:
            try:
                self.model = genai.GenerativeModel('gemini-1.5-pro')
            except:
                self.model = genai.GenerativeModel('gemini-pro')

        # Vector database
        self.vector_db = vector_db

        # Sohbet geçmişi
        self.chat_history = []

        # System prompt (Türkçe asistan karakteri)
        self.system_prompt = """Sen Mastercam CAD/CAM yazılımı için uzman bir Türkçe teknik destek asistanısın.

Görevin:
- Kullanıcılara Mastercam hakkında Türkçe sorularını yanıtlamak
- Verilen dokümantasyon bilgilerini kullanarak doğru ve açık cevaplar vermek
- Teknik terimleri açıklarken hem İngilizce hem Türkçe karşılıklarını vermek
- Eğer sorunun cevabı dokümantasyonda yoksa, bunu nazikçe belirtmek
- Mümkün olduğunca detaylı ve yardımcı olmak

Yanıt Stili:
- Açık ve anlaşılır Türkçe kullan
- Adım adım açıklamalar yap
- Örneklerle destekle
- Görsellerle ilişkili bilgileri vurgula

Sınırlamalar:
- Sadece verilen dokümantasyon bilgilerini kullan
- Emin olmadığın konularda tahmin yapma
- Mastercam dışı konularda yardımcı olamazsın
"""

    def search_documentation(self, query: str, n_results: int = 5) -> List[Dict]:
        """Dokümantasyonda arama yapar"""
        return self.vector_db.search(query, n_results=n_results)

    def format_context(self, search_results: List[Dict]) -> str:
        """Arama sonuçlarını context olarak formatlar"""
        if not search_results:
            return "İlgili dokümantasyon bulunamadı."

        context_parts = []
        for i, result in enumerate(search_results, 1):
            metadata = result['metadata']
            content = result['content']

            # Her doküman için context
            doc_context = f"""
--- Doküman {i} ---
Başlık: {metadata['title']}
Kategori: {metadata['category']}
Dosya: {metadata['file_path']}

İçerik:
{content[:1000]}  # İlk 1000 karakter

"""
            # Görseller varsa ekle
            images = metadata.get('images', [])
            if images:
                doc_context += f"İlgili Görseller: {', '.join(images[:3])}\n"

            context_parts.append(doc_context)

        return "\n".join(context_parts)

    def generate_response(self, user_question: str, context: str) -> str:
        """Gemini ile cevap üretir"""
        # Prompt oluştur
        prompt = f"""{self.system_prompt}

DOKÜMANTASYON BİLGİLERİ:
{context}

KULLANICI SORUSU:
{user_question}

TÜRKÇE YANITINIZ:"""

        try:
            # Gemini'ye sor
            response = self.model.generate_content(prompt)
            return response.text

        except Exception as e:
            return f"Üzgünüm, bir hata oluştu: {str(e)}"

    def chat(self, user_message: str) -> Dict:
        """
        Kullanıcı mesajını işler ve yanıt döner

        Args:
            user_message: Kullanıcı sorusu

        Returns:
            {
                'response': AI yanıtı,
                'sources': İlgili dökümanlar,
                'images': İlgili görseller
            }
        """
        # 1. Dokümantasyonda ara
        search_results = self.search_documentation(user_message, n_results=5)

        # 2. Context oluştur
        context = self.format_context(search_results)

        # 3. Gemini ile cevap üret
        response = self.generate_response(user_message, context)

        # 4. Görselleri topla
        all_images = []
        for result in search_results[:3]:  # İlk 3 doküman
            images = result['metadata'].get('images', [])
            all_images.extend(images[:2])  # Her doküman en fazla 2 görsel

        # 5. Kaynak dökümanları formatla
        sources = []
        for result in search_results[:3]:
            sources.append({
                'title': result['metadata']['title'],
                'file_path': result['metadata']['file_path'],
                'category': result['metadata']['category']
            })

        # Sohbet geçmişine ekle
        self.chat_history.append({
            'user': user_message,
            'assistant': response
        })

        return {
            'response': response,
            'sources': sources,
            'images': all_images[:5]  # Maksimum 5 görsel
        }

    def get_chat_history(self) -> List[Dict]:
        """Sohbet geçmişini döndürür"""
        return self.chat_history

    def clear_history(self):
        """Sohbet geçmişini temizler"""
        self.chat_history = []


if __name__ == "__main__":
    # Test
    import os
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("✗ GEMINI_API_KEY bulunamadı!")
        exit(1)

    # Vector DB yükle
    db = VectorDatabase()
    if not db.get_collection():
        print("✗ Vector database yüklenmedi!")
        exit(1)

    # Asistan oluştur
    assistant = MastercamAssistant(api_key, db)

    # Test sorusu
    result = assistant.chat("Mastercam'de 2D çizim nasıl yapılır?")

    print(f"\n🤖 Asistan Yanıtı:")
    print(result['response'])
    print(f"\n📚 Kaynaklar: {len(result['sources'])} doküman")
    print(f"🖼️ Görseller: {len(result['images'])} görsel")
