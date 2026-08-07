import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


# As variáveis precisam existir antes da importação da aplicação,
# porque settings é criado durante os imports.
os.environ["APP_NAME"] = "RH System API Test"
os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = (
    "postgresql+psycopg://rh_test:rh_test_password"
    "@test-database:5432/rh_system_test"
)
os.environ["JWT_SECRET_KEY"] = (
    "test-secret-key-only-for-automated-tests-123456789"
)
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"


from app.core.database import Base, get_db
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.user import User


TEST_DATABASE_URL = os.environ["DATABASE_URL"]

test_engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def create_test_database() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(autouse=True)
def clean_database() -> Generator[None, None, None]:
    yield

    with test_engine.begin() as connection:
        for table in reversed(Base.metadata.sorted_tables):
            connection.execute(table.delete())


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


def create_test_user(
    *,
    name: str,
    email: str,
    role: str,
    password: str = "SenhaSegura123",
    is_active: bool = True,
) -> User:
    with TestingSessionLocal() as db:
        user = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role=role,
            is_active=is_active,
        )

        db.add(user)
        db.commit()
        db.refresh(user)
        db.expunge(user)

        return user


def build_auth_headers(user: User) -> dict[str, str]:
    token = create_access_token(
        subject=str(user.id),
        additional_claims={
            "email": user.email,
            "role": user.role,
        },
    )

    return {
        "Authorization": f"Bearer {token}",
    }


@pytest.fixture()
def admin_user() -> User:
    return create_test_user(
        name="Administrador Teste",
        email="admin@test.com",
        role="admin",
    )


@pytest.fixture()
def rh_user() -> User:
    return create_test_user(
        name="RH Teste",
        email="rh@test.com",
        role="rh",
    )


@pytest.fixture()
def viewer_user() -> User:
    return create_test_user(
        name="Viewer Teste",
        email="viewer@test.com",
        role="viewer",
    )
@pytest.fixture()
def inactive_user() -> User:
    return create_test_user(
        name="Usuário Inativo Teste",
        email="inactive@test.com",
        role="viewer",
        password="SenhaInativa123",
        is_active=False,
    )
@pytest.fixture()
def admin_headers(
    admin_user: User,
) -> dict[str, str]:
    return build_auth_headers(admin_user)


@pytest.fixture()
def rh_headers(
    rh_user: User,
) -> dict[str, str]:
    return build_auth_headers(rh_user)


@pytest.fixture()
def viewer_headers(
    viewer_user: User,
) -> dict[str, str]:
    return build_auth_headers(viewer_user)