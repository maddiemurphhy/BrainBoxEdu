"""
Sets up the database connection. Locally this defaults to SQLite (a
single file on disk, studybuddy.db) -- zero setup, plenty for testing
on your own machine. In production (Vercel), DATABASE_URL is set to a
hosted Postgres instance instead, since Vercel's serverless functions
don't keep a persistent local disk between requests -- a SQLite file
there would get wiped constantly. Almost nothing else in the code had
to change to support this, which is the point of using SQLAlchemy here
instead of writing raw SQLite calls everywhere.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# check_same_thread=False is an SQLite-specific quirk needed because
# FastAPI can handle requests on different threads.
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Every model in models.py will inherit from this Base so SQLAlchemy
# knows to track it and can create its table.
Base = declarative_base()


def get_db():
    """
    FastAPI calls this once per request (see Depends(get_db) in the
    routers) and makes sure the database session is always closed
    afterwards, even if the request raised an error.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
