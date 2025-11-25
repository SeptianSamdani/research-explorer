from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.database import get_db
from app.models import Publication, Author, Topic, publication_authors, PublicationTopic
from app.schemas import PublicationResponse, PublicationDetail, PaginatedPublicationResponse
from typing import List, Optional

router = APIRouter()

@router.get("/", response_model=PaginatedPublicationResponse)
def get_publications(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    year: Optional[int] = Query(None),
    topic_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get paginated publications with optional filters
    
    Args:
        page: Page number (starting from 1)
        per_page: Items per page (max 100)
        year: Filter by publication year
        topic_id: Filter by topic ID
        search: Search in title and abstract
    """
    query = db.query(Publication)
    
    # Apply filters
    if year:
        query = query.filter(Publication.year == year)
    
    if topic_id:
        query = query.join(PublicationTopic).filter(PublicationTopic.topic_id == topic_id)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Publication.title.ilike(search_term),
                Publication.abstract.ilike(search_term)
            )
        )
    
    # Get total count
    total = query.count()
    
    # Calculate pagination
    skip = (page - 1) * per_page
    total_pages = (total + per_page - 1) // per_page
    
    # Get paginated results
    publications = query.order_by(
        Publication.year.desc(),
        Publication.id.desc()
    ).offset(skip).limit(per_page).all()
    
    return {
        "items": publications,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }

@router.get("/search")
def search_publications(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Quick search endpoint for autocomplete
    """
    search_term = f"%{q}%"
    
    results = db.query(Publication).filter(
        or_(
            Publication.title.ilike(search_term),
            Publication.abstract.ilike(search_term)
        )
    ).limit(limit).all()
    
    return {
        "query": q,
        "results": [
            {
                "id": pub.id,
                "title": pub.title,
                "year": pub.year
            }
            for pub in results
        ]
    }

@router.get("/stats")
def get_publication_stats(db: Session = Depends(get_db)):
    """Get statistics about publications"""
    
    total_pubs = db.query(func.count(Publication.id)).scalar()
    total_authors = db.query(func.count(func.distinct(Author.id))).scalar()
    total_topics = db.query(func.count(Topic.id)).scalar()
    
    pubs_by_year = db.query(
        Publication.year,
        func.count(Publication.id).label('count')
    ).filter(Publication.year != None).group_by(Publication.year).all()
    
    top_authors = db.query(
        Author.name,
        func.count(publication_authors.c.publication_id).label('pub_count')
    ).join(publication_authors).group_by(Author.id).order_by(
        func.count(publication_authors.c.publication_id).desc()
    ).limit(10).all()
    
    return {
        "total_publications": total_pubs,
        "total_authors": total_authors,
        "total_topics": total_topics,
        "publications_by_year": {str(year): count for year, count in pubs_by_year if year},
        "top_authors": [
            {"name": name, "count": count}
            for name, count in top_authors
        ]
    }

@router.get("/{publication_id}", response_model=PublicationDetail)
def get_publication(publication_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific publication"""
    pub = db.query(Publication).filter(Publication.id == publication_id).first()
    
    if not pub:
        raise HTTPException(status_code=404, detail="Publication not found")
    
    # Get topics for this publication
    topics = db.query(Topic).join(PublicationTopic).filter(
        PublicationTopic.publication_id == publication_id
    ).all()
    
    # FIXED: Explicitly load authors relationship
    from sqlalchemy.orm import joinedload
    pub = db.query(Publication).options(
        joinedload(Publication.authors)
    ).filter(Publication.id == publication_id).first()
    
    return {
        "id": pub.id,
        "title": pub.title,
        "abstract": pub.abstract,
        "year": pub.year,
        "source": pub.source,
        "url": pub.url,
        "authors": pub.authors,  # Now properly loaded
        "topics": topics
    }