import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./scouting.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    wyId = Column(Integer, unique=True, index=True)
    shortName = Column(String)
    firstName = Column(String)
    lastName = Column(String)
    birthDate = Column(String)
    positionCode = Column(String)
    
class PlayerStats(Base):
    __tablename__ = "player_stats"

    id = Column(Integer, primary_key=True, index=True)
    wyId = Column(Integer, unique=True, index=True)
    minutesOnField = Column(Integer)
    performance_score = Column(Float)
    
    # We can store a JSON string of all the P90 normalized stats if needed, 
    # but for this specific implementation we'll keep the score and some key metrics
    # Alternatively, we could define each stat as a column.
    normalized_stats = Column(String) # JSON dumped string of P90 stats
    
class MarketValueCache(Base):
    __tablename__ = "market_value_cache"

    id = Column(Integer, primary_key=True, index=True)
    wyId = Column(Integer, unique=True, index=True)
    market_value = Column(Integer, nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    role = Column(String, default="scout_basic")
    is_active = Column(Boolean, default=True)

def init_db():
    Base.metadata.create_all(bind=engine)
