"""
Vector Database Manager
ChromaDB kullanarak dökümanları vektörleştirir ve depolar
"""

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from typing import List, Dict
import json
from pathlib import Path


class VectorDatabase:
    """Dökümanları vektör veritabanında saklar ve arama yapar"""

    def __init__(self, persist_directory: str = "./data/chromadb"):
        """
        Args:
            persist_directory: ChromaDB'nin kaydedileceği klasör
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # ChromaDB client oluştur
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Embedding fonksiyonu (Türkçe destekli)
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )

        # Collection oluştur veya al
        self.collection = None

    def create_collection(self, collection_name: str = "mastercam_docs"):
        """Yeni bir collection oluşturur"""
        try:
            # Varsa sil
            try:
                self.client.delete_collection(name=collection_name)
            except:
                pass

            # Yeni collection oluştur
            self.collection = self.client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_function,
                metadata={"description": "Mastercam Türkçe Dokümantasyon"}
            )
            print(f"✓ Collection '{collection_name}' oluşturuldu")
        except Exception as e:
            print(f"✗ Collection oluşturma hatası: {e}")

    def get_collection(self, collection_name: str = "mastercam_docs"):
        """Var olan collection'ı alır"""
        try:
            self.collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            count = self.collection.count()
            print(f"✓ Collection yüklendi: {count} doküman")
            return True
        except Exception as e:
            print(f"✗ Collection bulunamadı: {e}")
            return False

    def add_documents(self, documents: List[Dict], batch_size: int = 100):
        """Dökümanları veritabanına ekler"""
        if not self.collection:
            print("✗ Collection oluşturulmamış!")
            return

        total = len(documents)
        print(f"Toplam {total} doküman ekleniyor...")

        # Batch halinde ekle
        for i in range(0, total, batch_size):
            batch = documents[i:i + batch_size]

            ids = []
            texts = []
            metadatas = []

            for idx, doc in enumerate(batch):
                doc_id = f"doc_{i + idx}"

                # Aranabilir metin: başlık + açıklama + içerik
                searchable_text = f"{doc['title']}\n{doc['description']}\n{doc['content']}"

                # Metadata
                metadata = {
                    'title': doc['title'],
                    'file_path': doc['file_path'],
                    'category': doc['category'],
                    'toc_path': doc.get('toc_path', ''),
                    'description': doc['description'][:500],  # ChromaDB limit
                    'images': json.dumps(doc['images'])  # JSON string olarak sakla
                }

                ids.append(doc_id)
                texts.append(searchable_text)
                metadatas.append(metadata)

            # Batch'i ekle
            try:
                self.collection.add(
                    ids=ids,
                    documents=texts,
                    metadatas=metadatas
                )
                print(f"  ✓ {i + len(batch)}/{total} doküman eklendi")
            except Exception as e:
                print(f"  ✗ Batch ekleme hatası: {e}")

        print(f"✓ Tüm dokümanlar eklendi!")

    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Sorgu ile ilgili dökümanları arar

        Args:
            query: Arama sorgusu
            n_results: Kaç sonuç döndürülecek

        Returns:
            İlgili dökümanların listesi
        """
        if not self.collection:
            print("✗ Collection yüklenmemiş!")
            return []

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )

            # Sonuçları formatla
            documents = []
            if results['documents'] and len(results['documents']) > 0:
                for i in range(len(results['documents'][0])):
                    doc = {
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else 0
                    }
                    # Images'i JSON'dan geri çevir
                    doc['metadata']['images'] = json.loads(doc['metadata'].get('images', '[]'))
                    documents.append(doc)

            return documents

        except Exception as e:
            print(f"✗ Arama hatası: {e}")
            return []

    def get_stats(self):
        """Veritabanı istatistiklerini döndürür"""
        if not self.collection:
            return {"status": "Collection yüklenmemiş"}

        count = self.collection.count()
        return {
            "total_documents": count,
            "collection_name": self.collection.name
        }


if __name__ == "__main__":
    # Test
    db = VectorDatabase()

    # Test: Collection oluştur
    db.create_collection()

    # Test döküman
    test_docs = [
        {
            'title': 'Test Doküman',
            'description': 'Bu bir test dokümanıdır',
            'content': 'Mastercam ile CNC programlama nasıl yapılır?',
            'file_path': 'test.htm',
            'category': 'Test',
            'toc_path': 'Test',
            'images': []
        }
    ]

    db.add_documents(test_docs)

    # Test arama
    results = db.search("CNC programlama")
    print(f"\nArama sonuçları: {len(results)} sonuç")
    for r in results:
        print(f"  - {r['metadata']['title']}")
