
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

connect_kwargs = {}
if settings.database_url.startswith("sqlite"):
    connect_kwargs["check_same_thread"] = False
else:
    connect_kwargs["sslmode"] = settings.database_ssl_mode

engine = create_engine(
    settings.database_url,
    connect_args=connect_kwargs,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Import models to register with SQLAlchemy metadata
from . import models  # noqa: F401
