from typing import List, Dict
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Publication, Author, Topic, PublicationTopic
from .openalex_fetcher import OpenAlexFetcher
from .preprocessor import preprocess_text
from .topic_modeling import train_topic_model
import json

class DataFetcher:
    def __init__(self, email: str = "your-email@example.com"):
        self.openalex = OpenAlexFetcher(email=email)
    
    def fetch_brin_publications(self, limit: int = 100, year_from: int = 2020) -> List[Dict]:
        """Fetch publikasi BRIN dari OpenAlex"""
        publications = self.openalex.search_brin_publications(
            limit=limit,
            year_from=year_from
        )
        return publications
    
    def save_to_database(self, publications: List[Dict], run_topic_modeling: bool = True):
        """
        Save publications ke database dengan topic modeling
        
        Args:
            publications: List of publication dicts
            run_topic_modeling: Jalankan topic modeling otomatis
        """
        db = SessionLocal()
        
        try:
            saved_count = 0
            
            for pub_data in publications:
                # Check duplicate by title
                exists = db.query(Publication).filter(
                    Publication.title == pub_data['title']
                ).first()
                
                if exists:
                    print(f"  Skipping duplicate: {pub_data['title'][:50]}...")
                    continue
                
                # Create publication
                pub = Publication(
                    title=pub_data['title'],
                    abstract=pub_data.get('abstract', ''),
                    year=pub_data.get('year'),
                    source=pub_data.get('source', 'OpenAlex'),
                    url=pub_data.get('url', '')
                )
                
                # Add authors with affiliations
                author_names = pub_data.get('authors', [])
                affiliations = pub_data.get('affiliations', [])
                
                for i, author_name in enumerate(author_names):
                    if not author_name or author_name == 'Unknown':
                        continue
                    
                    # Find or create author
                    author = db.query(Author).filter(
                        Author.name == author_name
                    ).first()
                    
                    if not author:
                        affiliation = affiliations[i] if i < len(affiliations) else None
                        author = Author(
                            name=author_name,
                            affiliation=affiliation
                        )
                        db.add(author)
                    
                    pub.authors.append(author)
                
                db.add(pub)
                saved_count += 1
            
            db.commit()
            print(f"✓ Saved {saved_count} new publications to database")
            
            # Run topic modeling if requested
            if run_topic_modeling and saved_count > 0:
                print("\nRunning topic modeling...")
                self._run_topic_modeling(db)
            
        except Exception as e:
            print(f"✗ Error saving to database: {e}")
            db.rollback()
            raise
        finally:
            db.close()
            self.openalex.close()
    
    def _run_topic_modeling(self, db: Session):
        """Run NMF topic modeling pada semua publikasi"""
        # Get all publications with abstracts
        publications = db.query(Publication).filter(
            Publication.abstract != None,
            Publication.abstract != ''
        ).all()
        
        if len(publications) < 5:
            print("Not enough publications for topic modeling (need at least 5)")
            return
        
        # Prepare documents
        documents = []
        pub_ids = []
        
        for pub in publications:
            text = f"{pub.title} {pub.abstract}"
            documents.append(text)
            pub_ids.append(pub.id)
        
        # Train topic model
        n_topics = min(10, len(publications) // 5)  # Dynamic topic count
        model, doc_topics, topics_keywords = train_topic_model(documents, n_topics)
        
        # Save topics
        for topic_data in topics_keywords:
            topic_name = f"Topic {topic_data['topic_id'] + 1}"
            keywords = ', '.join(topic_data['keywords'][:5])
            
            topic = Topic(
                name=topic_name,
                keywords=json.dumps(topic_data['keywords'])
            )
            db.add(topic)
            db.flush()
            
            # Assign publications to topics
            for pub_idx, topic_weight in enumerate(doc_topics[:, topic_data['topic_id']]):
                if topic_weight > 0.1:  # Threshold
                    pub_topic = PublicationTopic(
                        publication_id=pub_ids[pub_idx],
                        topic_id=topic.id,
                        probability=f"{topic_weight:.3f}"
                    )
                    db.add(pub_topic)
        
        db.commit()
        print(f"✓ Created {n_topics} topics")
    
    def get_statistics(self) -> Dict:
        """Get statistics dari fetched data"""
        db = SessionLocal()
        
        stats = {
            'total_publications': db.query(Publication).count(),
            'total_authors': db.query(Author).count(),
            'total_topics': db.query(Topic).count(),
            'publications_by_year': {},
            'top_authors': []
        }
        
        # Publications by year
        from sqlalchemy import func
        year_counts = db.query(
            Publication.year,
            func.count(Publication.id)
        ).group_by(Publication.year).all()
        
        stats['publications_by_year'] = {
            year: count for year, count in year_counts if year
        }
        
        # Top authors
        from app.models import publication_authors
        top_authors = db.query(
            Author.name,
            func.count(publication_authors.c.publication_id).label('pub_count')
        ).join(publication_authors).group_by(Author.id).order_by(
            func.count(publication_authors.c.publication_id).desc()
        ).limit(10).all()
        
        stats['top_authors'] = [
            {'name': name, 'publications': count}
            for name, count in top_authors
        ]
        
        db.close()
        return stats