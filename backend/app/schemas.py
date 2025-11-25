from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class AuthorBase(BaseModel):
    name: str
    affiliation: Optional[str] = None

class AuthorResponse(AuthorBase):
    id: int
    
    class Config:
        from_attributes = True

class TopicBase(BaseModel):
    name: str
    keywords: Optional[str] = None

class TopicResponse(TopicBase):
    id: int
    publication_count: Optional[int] = 0
    
    class Config:
        from_attributes = True

class PublicationBase(BaseModel):
    title: str
    abstract: Optional[str] = None
    year: Optional[int] = None
    source: Optional[str] = None
    url: Optional[str] = None

class PublicationResponse(PublicationBase):
    id: int
    authors: List[AuthorResponse] = []
    
    class Config:
        from_attributes = True

class PublicationDetail(PublicationResponse):
    """Extended publication info with topics"""
    topics: List[TopicResponse] = []
    
    class Config:
        from_attributes = True

class PaginatedPublicationResponse(BaseModel):
    """Paginated response wrapper"""
    items: List[PublicationResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool