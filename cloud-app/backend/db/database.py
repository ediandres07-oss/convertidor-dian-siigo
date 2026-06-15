import logging
from sqlalchemy import create_engine, Engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool

from backend.config import settings

logger = logging.getLogger(__name__)

# Create declarative base for models
Base = declarative_base()

# Create database engine
engine: Engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    echo=settings.DB_ECHO,
    future=True,
    connect_args={
        "connect_timeout": 10,
        "application_name": "cloudapp",
    }
)

# Create session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("SET client_encoding='UTF8'")
    cursor.close()


@event.listens_for(engine, "engine_disposed")
def receive_engine_disposed(engine):
    logger.info("Database engine disposed")


@event.listens_for(engine, "pool_connect")
def receive_pool_connect(dbapi_conn, connection_record):
    logger.debug("New database connection established")


def init_db():
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized")


def drop_db():
    """Drop all tables from the database (use with caution!)."""
    Base.metadata.drop_all(bind=engine)
    logger.warning("All database tables dropped")
