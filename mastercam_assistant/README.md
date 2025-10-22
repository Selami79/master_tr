# 🔧 Mastercam Türkçe Dokümantasyon Asistanı

Mastercam CAD/CAM yazılımı Türkçe dokümantasyonu için yapay zeka destekli akıllı asistan.

## ✨ Özellikler

- 🤖 **Google Gemini AI** ile güçlendirilmiş doğal dil anlama
- 📚 **2000+ HTML dokümantasyon** üzerinde RAG (Retrieval Augmented Generation)
- 🖼️ **3000+ görsel** ile zenginleştirilmiş yanıtlar
- 🇹🇷 **Tam Türkçe destek** - Hem sorular hem yanıtlar Türkçe
- 💬 **Sohbet arayüzü** - Streamlit tabanlı modern web UI
- 🔍 **Akıllı arama** - Semantic search ile en ilgili dökümanları bulur
- 📖 **Kaynak gösterimi** - Her yanıt için referans dökümanlar
- ⚡ **Hızlı ve kolay kurulum**

## 🎯 Kullanım Senaryoları

- "Mastercam'de 2D çizim nasıl yapılır?"
- "CNC torna programlama adımları neler?"
- "SOLIDWORKS dosyası nasıl içe aktarılır?"
- "Wireframe araçları nelerdir?"
- "Machine simulation nasıl kullanılır?"

## 🚀 Kurulum

### 1. Gereksinimler

- Python 3.8 veya üzeri
- 4GB+ RAM (dokümantasyon yükleme için)
- Google Gemini API anahtarı ([ücretsiz alın](https://makersuite.google.com/app/apikey))

### 2. Bağımlılıkları Yükleyin

```bash
cd mastercam_assistant
pip install -r requirements.txt
```

### 3. API Anahtarını Ayarlayın

```bash
# .env dosyası oluşturun
cp .env.example .env

# .env dosyasını düzenleyin ve API anahtarınızı ekleyin
# GEMINI_API_KEY=your_actual_api_key_here
```

### 4. Dokümantasyon Veritabanını Oluşturun

```bash
python scripts/setup_database.py
```

Bu işlem:
- Tüm HTML dosyalarını parse eder (~2100 doküman)
- İçerikleri vektörleştirir
- ChromaDB veritabanına yükler
- **Süre:** ~5-10 dakika (sisteme göre değişir)

### 5. Asistanı Başlatın

```bash
streamlit run app.py
```

Tarayıcınızda `http://localhost:8501` açılacaktır.

## 📁 Proje Yapısı

```
mastercam_assistant/
│
├── app.py                      # Streamlit web arayüzü
├── requirements.txt            # Python bağımlılıkları
├── .env.example               # Çevre değişkenleri şablonu
│
├── src/
│   └── gemini_assistant.py    # Gemini AI asistan
│
├── utils/
│   ├── html_parser.py         # HTML döküman parser
│   └── vector_db.py           # ChromaDB yöneticisi
│
├── scripts/
│   └── setup_database.py      # Veritabanı kurulum scripti
│
└── data/
    └── chromadb/              # Vektör veritabanı (otomatik oluşur)
```

## 🛠️ Teknoloji Stack'i

| Teknoloji | Kullanım Amacı |
|-----------|----------------|
| **Google Gemini 1.5 Flash** | Türkçe AI yanıt üretimi |
| **LangChain** | RAG framework |
| **ChromaDB** | Vektör veritabanı |
| **Streamlit** | Web arayüzü |
| **BeautifulSoup** | HTML parsing |
| **Sentence Transformers** | Türkçe embeddings |

## 💡 Nasıl Çalışır?

1. **Kullanıcı sorusu** → Web arayüzüne girilen Türkçe soru
2. **Vektör arama** → ChromaDB'de semantik benzerlik araması
3. **Context oluşturma** → En ilgili 5 doküman seçilir
4. **Gemini AI** → Context + soru ile Türkçe yanıt üretir
5. **Görsel ekleme** → İlgili dökümanların görselleri gösterilir
6. **Kaynak gösterimi** → Referans dökümanlar listelenir

## 🎨 Ekran Görüntüleri

### Ana Sohbet Arayüzü
```
┌─────────────────────────────────────────┐
│  🔧 Mastercam Türkçe Asistan            │
├─────────────────────────────────────────┤
│                                         │
│  👤 Siz: 2D çizim nasıl yapılır?       │
│                                         │
│  🤖 Asistan: Mastercam'de 2D çizim...  │
│                                         │
│  📚 Kaynak Dökümanlar [↓]              │
│  🖼️ İlgili Görseller [↓]               │
│                                         │
├─────────────────────────────────────────┤
│  [Sorunuzu buraya yazın...] [Gönder]   │
└─────────────────────────────────────────┘
```

## 🔧 Gelişmiş Kullanım

### Özel Parametre Ayarları

`app.py` dosyasında şu parametreleri ayarlayabilirsiniz:

```python
# Arama sonuç sayısı
n_results = 5  # 1-10 arası

# Görsel sayısı limiti
max_images = 5  # Gösterilecek maksimum görsel

# Vektör DB yolu
persist_directory = "./data/chromadb"
```

### Veritabanını Yeniden Oluşturma

Dokümantasyonda değişiklik yaptıysanız:

```bash
# Eski veritabanını sil
rm -rf mastercam_assistant/data/chromadb

# Yeniden oluştur
python mastercam_assistant/scripts/setup_database.py
```

## 🐛 Sorun Giderme

### "GEMINI_API_KEY bulunamadı" hatası
- `.env` dosyası oluşturduğunuzdan emin olun
- API anahtarınızı doğru girdiğinizi kontrol edin

### "Vector database yüklenmedi" hatası
- Önce `setup_database.py` scriptini çalıştırın
- Veritabanı yolu doğru olmalı

### Yavaş yanıtlar
- İlk sorguda embedding modeli yüklenir (normal)
- Gemini API kotanızı kontrol edin
- İnternet bağlantınızı kontrol edin

### Import hataları
- `pip install -r requirements.txt` komutunu çalıştırın
- Python sürümünüzü kontrol edin (3.8+)

## 📊 Performans

| Metrik | Değer |
|--------|-------|
| Toplam Döküman | ~2100 |
| Toplam Görsel | ~3000 |
| İlk Kurulum | 5-10 dakika |
| Sorgu Yanıt Süresi | 2-5 saniye |
| Veritabanı Boyutu | ~500 MB |
| RAM Kullanımı | ~2 GB |

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen:

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'feat: Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📝 Lisans

Bu proje MIT lisansı altındadır.

## 🙏 Teşekkürler

- **Google Gemini** - Ücretsiz AI API
- **Anthropic Claude** - Bu asistanı geliştirme yardımı
- **Mastercam** - Dokümantasyon kaynağı

## 📧 İletişim

Sorularınız için GitHub Issues kullanabilirsiniz.

---

**🎉 İyi Çalışmalar!**
