# RH System Lab

Laboratório DevOps com FastAPI, PostgreSQL e Adminer executados em Docker Compose.

## Arquitetura

- FastAPI: porta 8000
- Adminer: porta 8081
- PostgreSQL: acesso somente pela rede interna Docker
- Rede Docker: rh_network
- Volume persistente: rh_postgres_data

## Subir o ambiente

```bash
docker compose up -d --build


## Projeto RH System

Tecnologias utilizadas:

- FastAPI
- PostgreSQL
- Docker
- Docker Compose
- Git
- GitHub

Objetivo:

Construir um laboratório completo para estudos de DevOps, Cloud e Kubernetes.
