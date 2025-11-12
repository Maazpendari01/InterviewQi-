import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.database import Base
from app.services.db_service import DatabaseService


@pytest.fixture
def test_db():
    """Create test database"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()

    yield db

    db.close()


@pytest.fixture
def db_service(test_db):
    """Database service with test DB"""
    return DatabaseService(test_db)


@pytest.fixture
def sample_session(db_service):
    """Create sample interview session"""
    return db_service.create_session(
        session_id="test_123", category="coding", difficulty="medium"
    )
