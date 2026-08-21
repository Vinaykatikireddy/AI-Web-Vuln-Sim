import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.models.base import Base
from dotenv import load_dotenv 

load_dotenv()

# Create database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")