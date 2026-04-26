# API de Acompanhamento de Saúde Cardíaca

Backend do Sistema de Acompanhamento de Saúde Cardíaca, desenvolvido como
trabalho da disciplina de **Programação Modular**.

A API permite que usuários se cadastrem, autentiquem-se, registrem medições
cardiovasculares (pressão arterial, frequência cardíaca, oxigenação, peso e
sintomas) e gerem relatórios consolidados por período.

## Stack

- Python 3.12
- Flask (framework web)
- SQLite (banco em arquivo único)
- SQLAlchemy (ORM)
- JWT (autenticação)
- Marshmallow (validação)
- pytest (testes)

## Documentação da API

O contrato OpenAPI 3.0 está em [`docs/openapi.yaml`](docs/openapi.yaml). Pode
ser importado direto no Postman, Insomnia ou Swagger Editor.

## Como rodar

> Instruções completas serão adicionadas conforme o projeto evolui.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
