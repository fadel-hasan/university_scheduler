from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base

DB_PATH = "sqlite:///university_scheduler.db"

_engine = None
_session = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(DB_PATH, echo=False, future=True)
    return _engine

def get_session(engine=None):
    global _session
    if engine is None:
        engine = get_engine()
    if _session is None:
        _session = sessionmaker(bind=engine)()
    return _session

def create_tables(engine=None):
    if engine is None:
        engine = get_engine()
    Base.metadata.create_all(engine)
