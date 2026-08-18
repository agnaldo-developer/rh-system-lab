# RH System

Sistema de gestão de Recursos Humanos desenvolvido como aplicação de estudo para
DevOps, Cloud Computing e Platform Engineering.

## Estado atual

Baseline funcional: **v0.4.0**

A aplicação possui backend, frontend, autenticação, autorização, auditoria,
persistência em PostgreSQL e testes automatizados.

## Arquitetura da aplicação

```text
Frontend React/Vite
        |
        v
FastAPI REST API
        |
        v
PostgreSQL
