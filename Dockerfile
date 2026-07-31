# ===========================
# Stage 1 - Builder
# ===========================
FROM python:3.12-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /build

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
    --prefix=/install \
    -r requirements.txt
# ===========================
# Stage 2 - Runtime
# ===========================
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN groupadd -r appgroup && \
    useradd -r -g appgroup -d /code -s /usr/sbin/nologin appuser

WORKDIR /code

COPY --from=builder /install /usr/local

COPY --chown=appuser:appgroup app ./app

USER appuser

EXPOSE 8000

CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
