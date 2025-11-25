from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Topic, PublicationTopic, Publication
from typing import List

router = APIRouter()

@router.get("/")
def get_topics(db: Session = Depends(get_db)):
    """Get all topics with publication counts"""
    topics = db.query(
        Topic.id,
        Topic.name,
        Topic.keywords,
        func.count(PublicationTopic.id).label('publication_count')
    ).outerjoin(PublicationTopic).group_by(Topic.id).all()
    
    return [
        {
            "id": t.id,
            "name": t.name,
            "keywords": t.keywords,
            "publication_count": t.publication_count
        }
        for t in topics
    ]

@router.get("/trends")
def get_topic_trends(db: Session = Depends(get_db)):
    """Get topic distribution over years"""
    trends = db.query(
        Publication.year,
        Topic.name,
        func.count(PublicationTopic.id).label('count')
    ).join(
        PublicationTopic, Publication.id == PublicationTopic.publication_id
    ).join(
        Topic, PublicationTopic.topic_id == Topic.id
    ).filter(
        Publication.year != None
    ).group_by(
        Publication.year, Topic.name
    ).order_by(
        Publication.year, Topic.name
    ).all()
    
    return [
        {
            "year": t.year,
            "topic": t.name,
            "count": t.count
        }
        for t in trends
    ]