from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from docai.database.models import Base
from docai.database.config import DB_URL, POOL_SIZE, MAX_OVERFLOW

engine = create_engine(
    DB_URL,
    echo=True,  # log SQL queries for debugging purposes. Set to False later.
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """
    Initialize the database schema by creating all tables defined in the ORM models.

    Raises:
        Exception: If an error occurs during table creation.
    """
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        raise Exception(f"Error initializing the database: {e}") from e
