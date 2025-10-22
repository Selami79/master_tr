#!/bin/bash

echo "=================================="
echo "🚀 Mastercam Asistan Hızlı Kurulum"
echo "=================================="

# 1. .env kontrolü
if [ ! -f ".env" ]; then
    echo "📝 .env dosyası oluşturuluyor..."
    cp .env.example .env
    echo "⚠️  Lütfen .env dosyasına GEMINI_API_KEY anahtarınızı ekleyin!"
    echo "   https://makersuite.google.com/app/apikey"
    exit 1
fi

# 2. Bağımlılıkları kontrol et
echo "📦 Python paketleri kontrol ediliyor..."
pip install -r requirements.txt --quiet

# 3. Veritabanı kontrolü
if [ ! -d "data/chromadb" ]; then
    echo "🗄️  Veritabanı bulunamadı, oluşturuluyor..."
    echo "⏱️  Bu işlem 5-10 dakika sürebilir..."
    python scripts/setup_database.py
fi

# 4. Asistanı başlat
echo ""
echo "✅ Kurulum tamamlandı!"
echo "🌐 Web tarayıcınızda açılacak..."
echo ""
streamlit run app.py
