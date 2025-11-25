#!/usr/bin/env python3
"""
Script untuk inisialisasi database
Membuat semua tables yang diperlukan
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import engine, Base
from app.models import Publication, Author, Topic, PublicationTopic
from sqlalchemy import inspect, text

def check_database_connection():
    """Check if database is accessible"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure PostgreSQL is running")
        print("  2. Check DATABASE_URL in .env file")
        print("  3. Verify database 'brin_research_db' exists")
        return False

def check_existing_tables():
    """Check which tables already exist"""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if existing_tables:
        print(f"\n📋 Existing tables: {', '.join(existing_tables)}")
        return existing_tables
    else:
        print("\n📋 No tables found in database")
        return []

def create_tables():
    """Create all tables"""
    print("\n🔨 Creating database tables...")
    
    try:
        # Drop all tables first (optional - comment if you want to keep data)
        # Base.metadata.drop_all(bind=engine)
        # print("  • Dropped existing tables")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("  ✅ All tables created successfully!")
        
        # Verify tables were created
        inspector = inspect(engine)
        created_tables = inspector.get_table_names()
        
        print("\n📊 Created tables:")
        for table in created_tables:
            print(f"  • {table}")
        
        # Show table columns
        print("\n📋 Table structure:")
        for table in ['publications', 'authors', 'topics', 'publication_topics']:
            if table in created_tables:
                columns = inspector.get_columns(table)
                print(f"\n  {table}:")
                for col in columns:
                    print(f"    - {col['name']}: {col['type']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error creating tables: {e}")
        return False

def main():
    print("=" * 70)
    print("🗄️  DATABASE INITIALIZATION")
    print("=" * 70)
    
    # Step 1: Check connection
    print("\n1️⃣  Checking database connection...")
    if not check_database_connection():
        return
    
    # Step 2: Check existing tables
    print("\n2️⃣  Checking existing tables...")
    existing = check_existing_tables()
    
    # Step 3: Create tables
    if existing:
        confirm = input("\n⚠️  Tables already exist. Recreate? (yes/no): ")
        if confirm.lower() != 'yes':
            print("✅ Keeping existing tables")
            return
    
    print("\n3️⃣  Creating tables...")
    if create_tables():
        print("\n" + "=" * 70)
        print("✅ DATABASE INITIALIZATION COMPLETE!")
        print("=" * 70)
        print("\nYou can now:")
        print("  • Run seed data: python scripts/seed_data.py")
        print("  • Fetch data: python scripts/fetch_national_data.py")
    else:
        print("\n❌ Database initialization failed!")

if __name__ == "__main__":
    main()