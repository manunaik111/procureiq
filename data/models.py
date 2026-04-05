from sqlalchemy import create_engine, Column, String, Float, Integer, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

Base = declarative_base()


class ProcurementRecord(Base):
    __tablename__ = "procurement_records"

    request_id      = Column(String, primary_key=True)
    item            = Column(String, nullable=False)
    quantity        = Column(Integer, nullable=False)
    budget          = Column(Float, nullable=False)
    deadline        = Column(String)
    decision        = Column(String)
    po_number       = Column(String)
    rfq_reference   = Column(String)
    contract_ref    = Column(String)
    human_approved  = Column(Boolean, default=False)
    approver_notes  = Column(String, default="")
    created_at      = Column(String)
    completed_at    = Column(String)
    audit_log       = Column(JSON)


class SupplierRecord(Base):
    __tablename__ = "supplier_records"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    request_id      = Column(String, nullable=False)
    name            = Column(String)
    url             = Column(String)
    price           = Column(Float)
    risk_score      = Column(Float)
    notes           = Column(Text)
    selected        = Column(Boolean, default=False)


class SpendRecord(Base):
    __tablename__ = "spend_records"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    request_id      = Column(String, nullable=False)
    item            = Column(String)
    quantity        = Column(Integer)
    supplier_name   = Column(String)
    supplier_price  = Column(Float)
    market_avg      = Column(Float)
    total_spend     = Column(Float)
    total_savings   = Column(Float)
    savings_pct     = Column(Float)
    risk_score      = Column(Float)
    price_trend     = Column(String)
    po_number       = Column(String)
    completed_at    = Column(String)


def get_engine():
    # Use SQLite locally, PostgreSQL on Railway
    db_url = os.getenv("DATABASE_URL", "sqlite:///procureiq.db")
    
    # SQLite needs special connect_args
    if db_url.startswith("sqlite"):
        return create_engine(
            db_url,
            connect_args={"check_same_thread": False}
        )
    return create_engine(db_url)


def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def init_db():
    """Create all tables if they don't exist."""
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("Database tables created.")