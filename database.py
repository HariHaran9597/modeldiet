from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()

class RequestLog(Base):
    __tablename__ = "requests"
    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(String)
    tokens = Column(Integer)
    latency_ms = Column(Float)
    rate_limited = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

engine = create_engine("sqlite:///./modeldiet.db")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
