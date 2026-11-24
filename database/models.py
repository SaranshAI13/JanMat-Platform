"""
JanMat Platform — Database Schema & Data Models
Defines SQLAlchemy relational entities for constituencies, booths,
citizen feedback telemetry, and actionable campaign issue escalations.
"""

from datetime import datetime
from typing import Optional
import os
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, 
    Text, Boolean, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, scoped_session

Base = declarative_base()

class Constituency(Base):
    __tablename__ = 'constituencies'

    id = Column(String(32), primary_key=True)  # e.g., "UP_VARANASI", "MH_BARAMATI"
    name = Column(String(128), nullable=False, index=True)
    state = Column(String(64), nullable=False, index=True)
    zone = Column(String(32), nullable=False)   # North, Central, West, South
    priority_tier = Column(String(64), nullable=False) # Tier 1 - Battleground, Tier 2 - Lean, Tier 3 - Stronghold
    electorate_size = Column(Integer, default=1500000)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    booths = relationship("Booth", back_populates="constituency", cascade="all, delete-orphan")
    feedbacks = relationship("FeedbackTelemetry", back_populates="constituency", cascade="all, delete-orphan")
    issues = relationship("IssueLog", back_populates="constituency", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Constituency(id='{self.id}', name='{self.name}', state='{self.state}')>"


class Booth(Base):
    __tablename__ = 'booths'

    id = Column(Integer, primary_key=True, autoincrement=True)
    booth_number = Column(Integer, nullable=False)
    booth_name = Column(String(128), nullable=False)
    constituency_id = Column(String(32), ForeignKey('constituencies.id'), nullable=False, index=True)
    coordinator_name = Column(String(128), default="Ramesh Kumar")
    coordinator_phone = Column(String(32), default="+91 98765 43210")
    total_registered_voters = Column(Integer, default=1200)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    constituency = relationship("Constituency", back_populates="booths")
    feedbacks = relationship("FeedbackTelemetry", back_populates="booth", cascade="all, delete-orphan")
    issues = relationship("IssueLog", back_populates="booth", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_constituency_booth', 'constituency_id', 'booth_number', unique=True),
    )

    def __repr__(self):
        return f"<Booth(id={self.id}, num={self.booth_number}, name='{self.booth_name}')>"


class FeedbackTelemetry(Base):
    __tablename__ = 'feedback_telemetry'

    id = Column(Integer, primary_key=True, autoincrement=True)
    constituency_id = Column(String(32), ForeignKey('constituencies.id'), nullable=False, index=True)
    booth_id = Column(Integer, ForeignKey('booths.id'), nullable=False, index=True)
    demographic_cohort = Column(String(64), nullable=False, index=True) # Youth, Farmers, Women, Senior Citizens
    welfare_scheme_mentioned = Column(String(64), nullable=False, index=True) # PM-KISAN, Ayushman Bharat, etc.
    citizen_feedback_text = Column(Text, nullable=False)
    sentiment_score = Column(Float, nullable=False)  # Normalized -1.00 to +1.00
    sentiment_label = Column(String(32), nullable=False) # Positive, Neutral, Negative
    issue_category = Column(String(64), nullable=False, index=True) # Agriculture, Healthcare, Infra, Civic, Employment
    reporting_lag_hours = Column(Float, default=24.0) # Hours between ground observation & central sync
    is_offline_captured = Column(Boolean, default=False)
    reporting_timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    constituency = relationship("Constituency", back_populates="feedbacks")
    booth = relationship("Booth", back_populates="feedbacks")

    def __repr__(self):
        return f"<FeedbackTelemetry(id={self.id}, score={self.sentiment_score:.2f}, cohort='{self.demographic_cohort}')>"


class IssueLog(Base):
    __tablename__ = 'issues_log'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(String(32), unique=True, nullable=False, index=True) # e.g. JM-UP01-1002
    constituency_id = Column(String(32), ForeignKey('constituencies.id'), nullable=False, index=True)
    booth_id = Column(Integer, ForeignKey('booths.id'), nullable=False, index=True)
    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=False)
    issue_category = Column(String(64), nullable=False, index=True)
    priority = Column(String(32), nullable=False, index=True) # P0 - Critical, P1 - High, P2 - Medium, P3 - Low
    status = Column(String(32), nullable=False, default="Reported", index=True) # Reported, In Progress, Resolved
    assigned_to = Column(String(128), default="District Campaign Cell")
    sla_hours_limit = Column(Float, default=24.0) # SLA limit in hours (<24h standard)
    reported_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    sla_breached = Column(Boolean, default=False)

    # Relationships
    constituency = relationship("Constituency", back_populates="issues")
    booth = relationship("Booth", back_populates="issues")

    def __repr__(self):
        return f"<IssueLog(ticket='{self.ticket_id}', priority='{self.priority}', status='{self.status}')>"


# Database connection factory
def get_engine(db_path: Optional[str] = None):
    if not db_path:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)
        db_path = os.path.join(data_dir, 'janmat.db')
    return create_engine(f"sqlite:///{db_path}", echo=False, connect_args={"check_same_thread": False})

def init_db(engine=None):
    if engine is None:
        engine = get_engine()
    Base.metadata.create_all(engine)
    return engine

def get_session(engine=None):
    if engine is None:
        engine = get_engine()
    Session = scoped_session(sessionmaker(bind=engine))
    return Session()
