# backend/app/models.py
from sqlalchemy import Column, Integer, String, Text, Date, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

# Many-to-Many: Publication <-> Author
publication_authors = Table(
    'publication_authors', Base.metadata,
    Column('publication_id', Integer, ForeignKey('publications.id')),
    Column('author_id', Integer, ForeignKey('authors.id'))
)

class Publication(Base):
    __tablename__ = "publications"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    abstract = Column(Text)
    year = Column(Integer, index=True)
    source = Column(String)  # GARUDA/SINTA
    url = Column(String)
    
    authors = relationship("Author", secondary=publication_authors, back_populates="publications")
    topics = relationship("PublicationTopic", back_populates="publication")

class Author(Base):
    __tablename__ = "authors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    affiliation = Column(String)
    
    publications = relationship("Publication", secondary=publication_authors, back_populates="authors")

class Topic(Base):
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    keywords = Column(Text)  # JSON string
    
    publications = relationship("PublicationTopic", back_populates="topic")

class PublicationTopic(Base):
    __tablename__ = "publication_topics"
    
    id = Column(Integer, primary_key=True, index=True)
    publication_id = Column(Integer, ForeignKey('publications.id'))
    topic_id = Column(Integer, ForeignKey('topics.id'))
    probability = Column(String)  # Topic probability score
    
    publication = relationship("Publication", back_populates="topics")
    topic = relationship("Topic", back_populates="publications")