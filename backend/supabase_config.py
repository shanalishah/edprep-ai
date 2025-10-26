"""
Supabase Database Configuration
Replace the values below with your actual Supabase project details
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Supabase Database Configuration
# Get these values from your Supabase dashboard > Settings > Database
SUPABASE_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:[YOUR_PASSWORD]@db.[YOUR_PROJECT_REF].supabase.co:5432/postgres"
)

# Create SQLAlchemy engine
engine = create_engine(SUPABASE_DATABASE_URL)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)





