import sys
sys.path.append('.')

from app.database import SessionLocal, engine, Base
from app.models import Publication, Author, Topic, PublicationTopic
import json

# Create tables
Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    
    try:
        # Clear existing data
        db.query(PublicationTopic).delete()
        db.query(Publication).delete()
        db.query(Author).delete()
        db.query(Topic).delete()
        
        # Sample authors
        authors_data = [
            {"name": "Dr. Ahmad Hidayat", "affiliation": "BRIN - PRSDI"},
            {"name": "Dr. Siti Nurhaliza", "affiliation": "BRIN - PRSDI"},
            {"name": "Prof. Budi Santoso", "affiliation": "BRIN - Informatika"},
            {"name": "Dr. Dewi Lestari", "affiliation": "BRIN - PRSDI"},
        ]
        
        authors = []
        for data in authors_data:
            author = Author(**data)
            db.add(author)
            authors.append(author)
        
        db.commit()
        
        # Sample topics
        topics_data = [
            {"name": "Machine Learning", "keywords": json.dumps(["neural network", "deep learning", "classification", "regression"])},
            {"name": "Natural Language Processing", "keywords": json.dumps(["text mining", "sentiment analysis", "tokenization", "embedding"])},
            {"name": "Computer Vision", "keywords": json.dumps(["image processing", "object detection", "segmentation", "CNN"])},
            {"name": "Data Science", "keywords": json.dumps(["analytics", "visualization", "statistics", "big data"])},
        ]
        
        topics = []
        for data in topics_data:
            topic = Topic(**data)
            db.add(topic)
            topics.append(topic)
        
        db.commit()
        
        # Sample publications
        publications_data = [
            {
                "title": "Deep Learning untuk Klasifikasi Citra Medis",
                "abstract": "Penelitian ini mengembangkan model deep learning untuk klasifikasi citra medis dengan akurasi tinggi menggunakan arsitektur CNN.",
                "year": 2023,
                "source": "GARUDA",
                "url": "https://example.com/pub1",
                "author_ids": [0, 1],
                "topic_ids": [0, 2]
            },
            {
                "title": "Analisis Sentimen Media Sosial Menggunakan BERT",
                "abstract": "Studi tentang penerapan model BERT untuk analisis sentimen pada data media sosial berbahasa Indonesia.",
                "year": 2023,
                "source": "SINTA",
                "url": "https://example.com/pub2",
                "author_ids": [1, 2],
                "topic_ids": [1]
            },
            {
                "title": "Sistem Rekomendasi Berbasis Collaborative Filtering",
                "abstract": "Implementasi algoritma collaborative filtering untuk sistem rekomendasi produk e-commerce.",
                "year": 2024,
                "source": "GARUDA",
                "url": "https://example.com/pub3",
                "author_ids": [0, 3],
                "topic_ids": [0, 3]
            },
            {
                "title": "Deteksi Objek Real-time dengan YOLO",
                "abstract": "Pengembangan sistem deteksi objek real-time menggunakan algoritma YOLO untuk aplikasi surveillance.",
                "year": 2024,
                "source": "SINTA",
                "url": "https://example.com/pub4",
                "author_ids": [2, 3],
                "topic_ids": [2]
            },
            {
                "title": "Big Data Analytics untuk Smart City",
                "abstract": "Penerapan teknologi big data analytics dalam pengembangan konsep smart city di Indonesia.",
                "year": 2023,
                "source": "GARUDA",
                "url": "https://example.com/pub5",
                "author_ids": [0, 1, 2],
                "topic_ids": [3]
            },
        ]
        
        for pub_data in publications_data:
            author_ids = pub_data.pop("author_ids")
            topic_ids = pub_data.pop("topic_ids")
            
            pub = Publication(**pub_data)
            
            # Add authors
            for author_id in author_ids:
                pub.authors.append(authors[author_id])
            
            db.add(pub)
            db.commit()
            
            # Add topics with probabilities
            for topic_id in topic_ids:
                pub_topic = PublicationTopic(
                    publication_id=pub.id,
                    topic_id=topics[topic_id].id,
                    probability="0.85"
                )
                db.add(pub_topic)
        
        db.commit()
        print("✓ Data seeding completed successfully!")
        print(f"  - {len(authors)} authors created")
        print(f"  - {len(topics)} topics created")
        print(f"  - {len(publications_data)} publications created")
        
    except Exception as e:
        print(f"✗ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()