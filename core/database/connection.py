"""
Database connection and session management
Handles database initialization and provides session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import settings
from .models import Base

class DatabaseManager:
    """Manages database connections and sessions"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._initialized = False
    
    def initialize(self):
        """Initialize database connection"""
        if self._initialized:
            return
        
        if not settings.DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is required")
        
        self.engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=settings.DEBUG
        )
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        self._initialized = True
    
    def create_tables(self):
        """Create all database tables"""
        if not self._initialized:
            self.initialize()
        
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get database session"""
        if not self._initialized:
            self.initialize()
        
        return self.SessionLocal()
    
    def close_session(self, session):
        """Close database session"""
        if session:
            session.close()

# Global database manager
db_manager = DatabaseManager()

def get_db():
    """Dependency to get database session"""
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()

def init_db():
    """Initialize database and create tables"""
    db_manager.initialize()
    db_manager.create_tables()
    print("✓ Database initialized successfully!")