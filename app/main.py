from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.departments import router as departments_router
from app.api.routes.employees import router as employees_router
from app.api.routes.health import router as health_router
from app.api.routes.users import router as users_router
from app.api.routes.audit_logs import router as audit_logs_router
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.exception_handlers import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.core.middleware import RequestContextMiddleware
from app.core.logging_config import configure_logging


configure_logging()
app = FastAPI(
    title="RH System API",
    version="0.3.0",
    summary="Human Resources Management API",
    description="""
REST API para gerenciamento de departamentos,
funcionários e usuários.

Principais funcionalidades:

- Autenticação JWT
- Controle de acesso por papéis (RBAC)
- CRUD de departamentos
- CRUD de funcionários
- Gerenciamento de usuários
- Paginação
- Filtros
- Ordenação
- Request ID
- Logging estruturado
""",
    contact={
        "name": "Agnaldo Silva",
        "url": "https://github.com/agnaldo-developer",
    },
    license_info={
        "name": "MIT",
    },
)
app.add_middleware(RequestContextMiddleware)

app.add_exception_handler(
    HTTPException,
    http_exception_handler,
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.add_exception_handler(
    Exception,
    unhandled_exception_handler,
)

app.include_router(health_router)
app.include_router(departments_router, prefix="/api/v1")
app.include_router(employees_router, prefix="/api/v1")
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(audit_logs_router)
