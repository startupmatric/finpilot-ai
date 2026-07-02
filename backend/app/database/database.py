from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os
from app.config import DATABASE_URL

class Base(DeclarativeBase):
    pass

engine = create_engine(
    DATABASE_URL,
    echo=True,  # Shows SQL queries in console (good for development)
    pool_pre_ping=True,  # Recovers stale connections
    pool_size=10,  # Maximum connections in pool
    max_overflow=20  # Extra connections if pool is full
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()