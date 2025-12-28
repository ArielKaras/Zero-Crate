from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Uses Postgres in Production/Docker, but falls back to SQLite for local generic tests if needed (though we prefer Docker)
# "postgresql://user:password@db:5432/zerocrate"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/zerocrate_saas.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
