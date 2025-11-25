import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.openalex_fetcher import OpenAlexFetcher
from app.database import SessionLocal
from app.models import Publication, Author, Topic, PublicationTopic
import json
import argparse

def save_to_database(publications: list, db, run_topic_modeling: bool = True):
    """Save publications to database"""
    print("\n💾 Saving to database...")
    
    saved_count = 0
    skipped_count = 0
    
    for pub_data in publications:
        # Check duplicate
        exists = db.query(Publication).filter(
            Publication.title == pub_data['title']
        ).first()
        
        if exists:
            skipped_count += 1
            continue
        
        # Create publication
        pub = Publication(
            title=pub_data['title'],
            abstract=pub_data.get('abstract', ''),
            year=pub_data.get('year'),
            source=pub_data.get('source', 'OpenAlex'),
            url=pub_data.get('url', '')
        )
        
        # Add authors - prioritize Indonesian affiliations
        author_names = pub_data.get('authors', [])
        affiliations = pub_data.get('affiliations', [])
        
        for i, author_name in enumerate(author_names[:10]):
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
        
        # Commit every 50 records
        if saved_count % 50 == 0:
            db.commit()
            print(f"  Progress: {saved_count} saved, {skipped_count} skipped")
    
    db.commit()
    
    print(f"\n✅ Saved {saved_count} new publications")
    print(f"⏭️  Skipped {skipped_count} duplicates")
    
    # Run topic modeling
    if run_topic_modeling and saved_count > 0:
        print("\n🤖 Running topic modeling...")
        run_topic_modeling_process(db)
    
    return saved_count

def run_topic_modeling_process(db):
    """Run improved topic modeling"""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import LatentDirichletAllocation
    from app.services.preprocessor import preprocess_text
    
    # Get all publications with good abstracts
    publications = db.query(Publication).filter(
        Publication.abstract != None,
        Publication.abstract != '',
        Publication.abstract != 'No abstract available'
    ).all()
    
    # Filter only publications with substantial abstracts
    publications = [p for p in publications if len(p.abstract) > 100]
    
    if len(publications) < 10:
        print("❌ Not enough publications for topic modeling (need at least 10 with good abstracts)")
        return
    
    print(f"  Processing {len(publications)} publications...")
    
    # Prepare documents - combine title and abstract
    documents = []
    pub_ids = []
    
    for pub in publications:
        # Combine title (weighted more) and abstract
        text = f"{pub.title} {pub.title} {pub.abstract}"
        documents.append(text)
        pub_ids.append(pub.id)
    
    # Preprocess
    print("  Preprocessing texts...")
    cleaned_docs = [preprocess_text(doc) for doc in documents]
    
    # Remove empty docs
    valid_docs = []
    valid_pub_ids = []
    for i, doc in enumerate(cleaned_docs):
        if len(doc.split()) >= 10:  # At least 10 words
            valid_docs.append(doc)
            valid_pub_ids.append(pub_ids[i])
    
    if len(valid_docs) < 10:
        print(f"❌ Not enough valid documents after preprocessing ({len(valid_docs)})")
        return
    
    print(f"  Valid documents: {len(valid_docs)}")
    
    # Vectorize with better parameters
    print("  Vectorizing...")
    vectorizer = TfidfVectorizer(
        max_features=500,
        min_df=2,
        max_df=0.7,
        ngram_range=(1, 2),
        stop_words='english'
    )
    
    try:
        tfidf = vectorizer.fit_transform(valid_docs)
    except ValueError as e:
        print(f"❌ Vectorization error: {e}")
        return
    
    # Dynamic topic count
    n_topics = min(12, max(5, len(valid_docs) // 15))
    
    print(f"  Training LDA with {n_topics} topics...")
    
    # Use LDA instead of NMF for better results
    lda = LatentDirichletAllocation(
        n_components=n_topics,
        max_iter=50,
        learning_method='online',
        random_state=42,
        n_jobs=-1
    )
    
    doc_topics = lda.fit_transform(tfidf)
    
    # Clear old topics
    db.query(PublicationTopic).delete()
    db.query(Topic).delete()
    db.commit()
    
    # Extract and save topics
    feature_names = vectorizer.get_feature_names_out()
    
    print(f"\n  📋 Discovered Topics:")
    
    for topic_idx, topic in enumerate(lda.components_):
        # Get top keywords
        top_indices = topic.argsort()[-10:][::-1]
        top_keywords = [feature_names[i] for i in top_indices]
        top_weights = topic[top_indices]
        
        # Filter out common/generic words
        filtered_keywords = []
        for kw in top_keywords:
            if len(kw) > 3 and kw not in ['data', 'study', 'research', 'analysis', 'results']:
                filtered_keywords.append(kw)
        
        if len(filtered_keywords) < 3:
            filtered_keywords = top_keywords[:5]
        
        # Create descriptive name
        descriptive_name = ' / '.join(filtered_keywords[:3]).title()
        
        print(f"    Topic {topic_idx + 1}: {', '.join(filtered_keywords[:5])}")
        
        topic_obj = Topic(
            name=descriptive_name[:100],  # Limit length
            keywords=json.dumps(filtered_keywords[:10])
        )
        db.add(topic_obj)
        db.flush()
        
        # Assign publications to topics
        for pub_idx, topic_weight in enumerate(doc_topics[:, topic_idx]):
            if topic_weight > 0.05:  # Threshold
                pub_topic = PublicationTopic(
                    publication_id=valid_pub_ids[pub_idx],
                    topic_id=topic_obj.id,
                    probability=f"{topic_weight:.4f}"
                )
                db.add(pub_topic)
    
    db.commit()
    print(f"\n✅ Created {n_topics} topics with LDA")

def get_statistics(db):
    """Get database statistics"""
    from sqlalchemy import func
    from app.models import publication_authors
    
    stats = {
        'total_publications': db.query(Publication).count(),
        'total_authors': db.query(Author).count(),
        'total_topics': db.query(Topic).count(),
        'publications_by_year': {},
        'top_authors': [],
        'top_institutions': {}
    }
    
    # Publications by year
    year_counts = db.query(
        Publication.year,
        func.count(Publication.id)
    ).group_by(Publication.year).all()
    
    stats['publications_by_year'] = {
        year: count for year, count in year_counts if year
    }
    
    # Top authors
    top_authors = db.query(
        Author.name,
        Author.affiliation,
        func.count(publication_authors.c.publication_id).label('pub_count')
    ).join(publication_authors).group_by(
        Author.id, Author.name, Author.affiliation
    ).order_by(
        func.count(publication_authors.c.publication_id).desc()
    ).limit(15).all()
    
    stats['top_authors'] = [
        {'name': name, 'affiliation': aff, 'publications': count}
        for name, aff, count in top_authors
    ]
    
    # Count by institution (from affiliations)
    for author in top_authors:
        if author[1]:  # affiliation
            inst = author[1].split(',')[0][:30]  # First part of affiliation
            stats['top_institutions'][inst] = stats['top_institutions'].get(inst, 0) + 1
    
    return stats

def main():
    parser = argparse.ArgumentParser(
        description='Fetch Indonesian National Research Publications (IMPROVED)'
    )
    parser.add_argument(
        '--limit', 
        type=int, 
        default=500, 
        help='Maximum publications to fetch (default: 500)'
    )
    parser.add_argument(
        '--year-from', 
        type=int, 
        default=2020, 
        help='Fetch from this year (default: 2020)'
    )
    parser.add_argument(
        '--year-to',
        type=int,
        default=None,
        help='Fetch until this year (default: current year)'
    )
    parser.add_argument(
        '--email', 
        type=str, 
        default='research@example.com', 
        help='Your email for OpenAlex polite pool'
    )
    parser.add_argument(
        '--institutions',
        nargs='+',
        help='Specific institutions (e.g., UI ITB UGM BRIN)'
    )
    parser.add_argument(
        '--fields',
        nargs='+',
        help='Research fields (e.g., "Computer Science" Medicine)'
    )
    parser.add_argument(
        '--no-topics', 
        action='store_true', 
        help='Skip topic modeling'
    )
    parser.add_argument(
        '--test', 
        action='store_true', 
        help='Test API connection only'
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🇮🇩 INDONESIAN RESEARCH PUBLICATIONS FETCHER (IMPROVED)")
    print("=" * 70)
    
    fetcher = OpenAlexFetcher(email=args.email)
    
    # Test connection
    if args.test:
        success = fetcher.test_connection()
        fetcher.close()
        return
    
    # Fetch publications
    try:
        publications = fetcher.fetch_indonesian_publications(
            limit=args.limit,
            year_from=args.year_from,
            year_to=args.year_to,
            institutions=args.institutions,
            fields=args.fields
        )
        
        if not publications:
            print("\n❌ No publications found!")
            print("\nTroubleshooting:")
            print("  1. Try with --test to check API connection")
            print("  2. Try increasing --limit")
            print("  3. Try different year range")
            return
        
        # Save to database
        db = SessionLocal()
        try:
            saved = save_to_database(
                publications, 
                db, 
                run_topic_modeling=not args.no_topics
            )
            
            if saved > 0:
                # Show statistics
                print("\n" + "=" * 70)
                print("📊 DATABASE STATISTICS")
                print("=" * 70)
                
                stats = get_statistics(db)
                
                print(f"\n📚 Total Publications: {stats['total_publications']}")
                print(f"👥 Total Authors: {stats['total_authors']}")
                print(f"🏷️  Total Topics: {stats['total_topics']}")
                
                print("\n📅 Publications by Year:")
                for year in sorted(stats['publications_by_year'].keys(), reverse=True):
                    count = stats['publications_by_year'][year]
                    bar = "█" * (count // 10) if count > 0 else ""
                    print(f"  {year}: {count:4} {bar}")
                
                print("\n🏆 Top 10 Most Prolific Authors:")
                for i, author in enumerate(stats['top_authors'][:10], 1):
                    aff = (author['affiliation'] or 'N/A')[:30]
                    print(f"  {i:2}. {author['name']:35} ({aff}) - {author['publications']} pubs")
                
                if stats['top_institutions']:
                    print("\n🏛️  Top Institutions (by author count):")
                    sorted_inst = sorted(
                        stats['top_institutions'].items(),
                        key=lambda x: x[1],
                        reverse=True
                    )
                    for inst, count in sorted_inst[:10]:
                        print(f"  • {inst}: {count}")
                
        finally:
            db.close()
        
    finally:
        fetcher.close()
    
    print("\n" + "=" * 70)
    print("✅ FETCHING COMPLETED!")
    print("=" * 70)

if __name__ == "__main__":
    main()