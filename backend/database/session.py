from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from config import get_settings
from models.events import Base
import logging

logger = logging.getLogger(__name__)

settings = get_settings()

engine = create_engine(
    settings.sqlalchemy_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables() -> None:
    """Crea las tablas de App 2 si no existen (no toca tablas de App 1)."""
    Base.metadata.create_all(bind=engine)
    logger.info("Tablas de métricas verificadas/creadas.")


@contextmanager
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db_dep():
    """Dependency de FastAPI."""
    with get_db() as db:
        yield db
