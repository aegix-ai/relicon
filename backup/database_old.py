"""Database configuration and models for Relicon feedback loop."""
import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Date, BigInteger, Boolean, Text, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///relicon.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class MetricsMeta(Base):
    """Facebook/Meta advertising metrics."""
    __tablename__ = "metrics_meta"
    
    id = Column(Integer, primary_key=True, index=True)
    ad_id = Column(Integer, nullable=False, index=True)
    date = Column(Date, nullable=False)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    spend = Column(Numeric(10, 2), default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class MetricsTT(Base):
    """TikTok advertising metrics."""
    __tablename__ = "metrics_tt"
    
    id = Column(Integer, primary_key=True, index=True)
    ad_id = Column(String(255), nullable=False, index=True)
    date = Column(Date, nullable=False)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    spend = Column(Numeric(10, 2), default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class Sales(Base):
    """Sales/conversion tracking from Shopify."""
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(BigInteger, nullable=False, unique=True)
    ad_code = Column(Text, nullable=True)  # UTM content
    revenue = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Ads(Base):
    """Ads table for tracking creative performance."""
    __tablename__ = "ads"
    
    id = Column(Integer, primary_key=True, index=True)
    ad_id = Column(String(255), nullable=False, unique=True)
    platform = Column(String(50), nullable=False)  # 'meta', 'tiktok', etc.
    creative_content = Column(Text, nullable=True)
    winner_tag = Column(Boolean, default=False)
    roas = Column(Numeric(10, 2), default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database tables created successfully!")