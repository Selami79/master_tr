"""
Vector Database Kurulum Scripti
Dökümanları parse edip ChromaDB'ye yükler
"""

import sys
from pathlib import Path
import time

# Üst dizini path'e ekle
sys.path.append(str(Path(__file__).parent.parent))

from utils.html_parser import DocumentationParser
from utils.vector_db import VectorDatabase


def main():
    """Ana kurulum fonksiyonu"""

    print("=" * 60)
    print("🚀 MASTERCAM DOKÜMANTASYON VERİTABANI KURULUMU")
    print("=" * 60)

    # 1. HTML Parser
    print("\n📄 Adım 1: HTML Dökümanları Parse Ediliyor...")

    # tr/ klasörünü otomatik bul
    # Script: D:\MASTERCAM2025\mastercam_assistant\scripts\setup_database.py
    # tr/ klasörü: D:\MASTERCAM2025\tr
    script_dir = Path(__file__).parent  # scripts/
    project_root = script_dir.parent.parent  # D:\MASTERCAM2025\
    docs_path = project_root / "tr"

    print(f"📂 Dokümantasyon klasörü: {docs_path}")

    if not docs_path.exists():
        print(f"❌ Hata: {docs_path} bulunamadı!")
        print(f"\n💡 İpucu: 'tr' klasörü şurada olmalı: {project_root}")
        return

    parser = DocumentationParser(docs_path)
    start_time = time.time()
    documents = parser.parse_all_documents()
    parse_time = time.time() - start_time

    print(f"✅ {len(documents)} doküman parse edildi ({parse_time:.2f} saniye)")

    if len(documents) == 0:
        print("❌ Hata: Hiç doküman bulunamadı!")
        return

    # 2. Vector Database Kurulumu
    print("\n🗄️ Adım 2: Vector Database Oluşturuluyor...")
    # ChromaDB klasörünü mastercam_assistant/data/chromadb içinde oluştur
    db_path = script_dir.parent / "data" / "chromadb"
    db = VectorDatabase(persist_directory=str(db_path))

    # Collection oluştur
    db.create_collection("mastercam_docs")

    # 3. Dökümanları Yükle
    print("\n📥 Adım 3: Dökümanlar Veritabanına Yükleniyor...")
    start_time = time.time()
    db.add_documents(documents, batch_size=50)
    load_time = time.time() - start_time

    print(f"✅ Yükleme tamamlandı ({load_time:.2f} saniye)")

    # 4. Test Arama
    print("\n🔍 Adım 4: Test Araması Yapılıyor...")
    test_queries = [
        "2D çizim",
        "CNC programlama",
        "machine simulation"
    ]

    for query in test_queries:
        results = db.search(query, n_results=3)
        print(f"\n  Sorgu: '{query}' -> {len(results)} sonuç")
        if results:
            print(f"    En ilgili: {results[0]['metadata']['title']}")

    # 5. İstatistikler
    print("\n" + "=" * 60)
    print("📊 KURULUM TAMAMLANDI!")
    print("=" * 60)
    stats = db.get_stats()
    print(f"✓ Toplam Doküman: {stats['total_documents']}")
    print(f"✓ Collection: {stats['collection_name']}")
    print(f"✓ Parse Süresi: {parse_time:.2f} saniye")
    print(f"✓ Yükleme Süresi: {load_time:.2f} saniye")
    print(f"✓ Toplam Süre: {(parse_time + load_time):.2f} saniye")
    print("\n🎉 Artık asistanı başlatabilirsiniz!")
    print("   Komut: streamlit run mastercam_assistant/app.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
