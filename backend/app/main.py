from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api import publications, topics
import os
from dotenv import load_dotenv

load_dotenv()

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BRIN Research Explorer API",
    description="API for BRIN publication topic analysis",
    version="1.0.0"
)

# CORS
origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(publications.router, prefix="/api/publications", tags=["Publications"])
app.include_router(topics.router, prefix="/api/topics", tags=["Topics"])

@app.get("/")
def read_root():
    return {"message": "BRIN Research Explorer API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}