# backend/scripts/ingest_data.py
from app.database import SessionLocal
from app.models import Publication, Author
from app.services.scraper import scrape_garuda_sample
import pandas as pd

def ingest_publications():
    db = SessionLocal()
    df = scrape_garuda_sample()
    
    for _, row in df.iterrows():
        pub = Publication(
            title=row['title'],
            abstract=row['abstract'],
            year=row['year'],
            source=row['source'],
            url=row.get('url', '')
        )
        db.add(pub)
    
    db.commit()
    db.close()
    print(f"Ingested {len(df)} publications")

if __name__ == "__main__":
    ingest_publications()