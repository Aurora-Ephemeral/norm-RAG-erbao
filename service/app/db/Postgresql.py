from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core import settings


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class PostgreSQLSession:
    @staticmethod
    def get_session() -> Session:
        return SessionLocal()

    @staticmethod
    def close_session(db: Session) -> None:
        db.close()

    @staticmethod
    def rollback(db: Session) -> None:
        db.rollback()


def get_db():
    db = PostgreSQLSession.get_session()
    try:
        yield db
    except Exception:
        PostgreSQLSession.rollback(db)
        raise
    finally:
        PostgreSQLSession.close_session(db)
