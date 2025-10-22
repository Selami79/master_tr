"""
HTML Dokümantasyon Parser
Mastercam dokümantasyon HTML dosyalarını parse eder
"""

import os
import re
from bs4 import BeautifulSoup
from pathlib import Path
from typing import Dict, List, Optional
from tqdm import tqdm


class DocumentationParser:
    """MadCap Flare HTML dokümantasyonunu parse eder"""

    def __init__(self, docs_path: str):
        """
        Args:
            docs_path: tr/ klasörünün yolu
        """
        self.docs_path = Path(docs_path)
        self.content_path = self.docs_path / "Content"

    def find_all_html_files(self) -> List[Path]:
        """Tüm HTML dosyalarını bulur"""
        html_files = []
        for root, dirs, files in os.walk(self.content_path):
            for file in files:
                if file.endswith('.htm') or file.endswith('.html'):
                    html_files.append(Path(root) / file)
        return html_files

    def extract_images_from_html(self, html_content: str, html_file_path: Path) -> List[str]:
        """HTML içeriğinden resim yollarını çıkarır"""
        soup = BeautifulSoup(html_content, 'html.parser')
        images = []

        # img tag'lerini bul
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                # Relative path'i absolute path'e çevir
                img_path = (html_file_path.parent / src).resolve()
                if img_path.exists():
                    # tr/ klasörüne göre relative path
                    rel_path = img_path.relative_to(self.docs_path)
                    images.append(str(rel_path))

        return images

    def clean_text(self, text: str) -> str:
        """Metni temizler"""
        # Fazla boşlukları temizle
        text = re.sub(r'\s+', ' ', text)
        # Başta ve sonda boşluk
        text = text.strip()
        return text

    def parse_html_file(self, file_path: Path) -> Optional[Dict]:
        """Tek bir HTML dosyasını parse eder"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            soup = BeautifulSoup(html_content, 'html.parser')

            # Title çıkar
            title = soup.find('title')
            title_text = title.get_text() if title else file_path.stem

            # Meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc.get('content', '') if meta_desc else ''

            # Ana içeriği çıkar (body içindeki text)
            body = soup.find('body')
            if not body:
                return None

            # Script ve style tag'lerini kaldır
            for script in body(['script', 'style', 'nav', 'header', 'footer']):
                script.decompose()

            # Text içeriği al
            text_content = body.get_text()
            text_content = self.clean_text(text_content)

            # İçerik çok kısa ise atla
            if len(text_content) < 50:
                return None

            # Görselleri çıkar
            images = self.extract_images_from_html(html_content, file_path)

            # TOC path (breadcrumb)
            toc_path = soup.find('html').get('data-mc-toc-path', '') if soup.find('html') else ''

            # Relative file path
            rel_path = file_path.relative_to(self.docs_path)

            return {
                'file_path': str(rel_path),
                'title': self.clean_text(title_text),
                'description': self.clean_text(description),
                'content': text_content,
                'images': images,
                'toc_path': toc_path,
                'category': self.get_category_from_path(file_path)
            }

        except Exception as e:
            print(f"Hata ({file_path}): {e}")
            return None

    def get_category_from_path(self, file_path: Path) -> str:
        """Dosya yolundan kategori çıkarır"""
        try:
            rel_path = file_path.relative_to(self.content_path)
            parts = rel_path.parts
            if len(parts) > 1:
                return parts[0]  # İlk klasör adı (Machine, Wireframe, vb.)
            return "General"
        except:
            return "General"

    def parse_all_documents(self) -> List[Dict]:
        """Tüm dokümantasyonu parse eder"""
        html_files = self.find_all_html_files()
        print(f"Toplam {len(html_files)} HTML dosyası bulundu")

        documents = []
        for file_path in tqdm(html_files, desc="Dokümantasyon parse ediliyor"):
            doc = self.parse_html_file(file_path)
            if doc:
                documents.append(doc)

        print(f"\n✓ {len(documents)} doküman başarıyla parse edildi")
        return documents


if __name__ == "__main__":
    # Test
    parser = DocumentationParser("/home/user/master_tr/tr")
    docs = parser.parse_all_documents()

    # İlk 3 dokümanı göster
    for i, doc in enumerate(docs[:3]):
        print(f"\n--- Doküman {i+1} ---")
        print(f"Başlık: {doc['title']}")
        print(f"Kategori: {doc['category']}")
        print(f"İçerik (ilk 200 karakter): {doc['content'][:200]}...")
        print(f"Görsel sayısı: {len(doc['images'])}")
