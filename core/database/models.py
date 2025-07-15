"""
Database models for Relicon AI Video Generation Platform
Defines all database tables and relationships
"""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date, BigInteger, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Ads(Base):
    """Ads table for tracking creative performance"""
    __tablename__ = "ads"
    
    id = Column(Integer, primary_key=True, index=True)
    ad_id = Column(String(255), nullable=False, unique=True)
    platform = Column(String(50), nullable=False)  # 'meta', 'tiktok', etc.
    creative_content = Column(Text, nullable=True)
    winner_tag = Column(Boolean, default=False)
    roas = Column(Numeric(10, 2), default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Ad(id={self.id}, ad_id={self.ad_id}, platform={self.platform})>"

class Sales(Base):
    """Sales/conversion tracking from Shopify"""
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(BigInteger, nullable=False, unique=True)
    ad_code = Column(Text, nullable=True)  # UTM content
    revenue = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Sale(id={self.id}, order_id={self.order_id}, revenue={self.revenue})>"

class MetricsMeta(Base):
    """Facebook/Meta advertising metrics"""
    __tablename__ = "metrics_meta"
    
    id = Column(Integer, primary_key=True, index=True)
    ad_id = Column(Integer, nullable=False, index=True)
    date = Column(Date, nullable=False)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    spend = Column(Numeric(10, 2), default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<MetricsMeta(ad_id={self.ad_id}, date={self.date})>"

class MetricsTT(Base):
    """TikTok advertising metrics"""
    __tablename__ = "metrics_tt"
    
    id = Column(Integer, primary_key=True, index=True)
    ad_id = Column(String(255), nullable=False, index=True)
    date = Column(Date, nullable=False)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    spend = Column(Numeric(10, 2), default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<MetricsTT(ad_id={self.ad_id}, date={self.date})>"