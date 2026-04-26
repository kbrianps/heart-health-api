# API de Acompanhamento de Saúde Cardíaca

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat&logo=sqlite&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat&logo=sqlalchemy&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-Auth-000000?style=flat&logo=jsonwebtokens&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-8.3-0A9EDC?style=flat&logo=pytest&logoColor=white)
![OpenAPI](https://img.shields.io/badge/OpenAPI-3.0-6BA539?style=flat&logo=openapiinitiative&logoColor=white)
![License](https://img.shields.io/badge/license-GPLv3-blue?style=flat)

Backend do Sistema de Acompanhamento de Saúde Cardíaca, desenvolvido como
trabalho da disciplina de **Programação Modular**.

A API permite que usuários se cadastrem, autentiquem-se, registrem medições
cardiovasculares (pressão arterial, frequência cardíaca, oxigenação, peso e
sintomas) e gerem relatórios consolidados por período.

## Equipe

Trabalho desenvolvido pelos seguintes alunos:

- [Brian Kévin dos Santos Pravato](https://github.com/kbrianps)
- José Henrique de Souza Furtado
- Pedro Levi Freitas Nascimento
- [Natalha da Silva Santanna](https://github.com/NatalhaSantanna)

## Stack

**Linguagem:** Python 3.12

**Framework web:** Flask
- Microframework leve e simples
- Define rotas HTTP, recebe requisições JSON e retorna respostas JSON

**Banco de dados:** SQLite
- Banco em arquivo único (`app.db`), zero configuração
- Não precisa instalar servidor de banco, funciona em qualquer máquina
- Apagar o arquivo equivale a resetar o banco

**ORM (Object-Relational Mapper):** SQLAlchemy + Flask-SQLAlchemy
- Permite trabalhar com tabelas como se fossem classes Python
- Em vez de SQL puro, a gente escreve `User.query.filter_by(email=...)`

**Autenticação:** JWT (JSON Web Tokens) via Flask-JWT-Extended
- Login devolve um token que o cliente guarda
- Em cada requisição protegida, o cliente envia o token no header
  `Authorization: Bearer <token>`
- O servidor valida o token e identifica o usuário sem novas consultas ao banco

**Hash de senha:** Werkzeug (já vem com o Flask)
- Senhas nunca ficam em texto puro no banco
- Usa hash com salt para proteger contra vazamentos

**Validação de dados:** Marshmallow
- Define schemas que descrevem o formato esperado de cada request
- Valida automaticamente campos obrigatórios, tipos, ranges (ex: pressão
  sistólica entre 50 e 250) e formato de e-mail
- Retorna mensagens de erro padronizadas

**CORS:** Flask-Cors
- Libera o backend para receber requisições do app Ionic/Capacitor que
  rodará no celular Android

**Testes:** pytest
- Framework de testes mais usado em Python
- Testes unitários: testam funções isoladas (services), sem subir o app
- Testes de integração: sobem o app inteiro com banco em memória e testam
  as rotas via cliente HTTP

**Documentação da API:** OpenAPI 3.0 (Swagger) via flask-swagger-ui
- Especificação em [`docs/openapi.yaml`](docs/openapi.yaml) define todas as
  rotas, requests e responses
- UI interativa em `http://localhost:3000/docs` permite testar a API direto
  no navegador

## Arquitetura: Modularização por Feature

O código é organizado **por feature**: cada funcionalidade tem sua própria
pasta com tudo o que precisa, em vez de organizar por tipo de arquivo.
Isso atende ao que a disciplina de Programação Modular cobra: módulos com
fronteiras claras e baixo acoplamento.

```
app/
├── __init__.py              app factory: cria Flask, registra blueprints
├── config.py                configurações por ambiente (dev/test/prod)
├── extensions.py            instâncias de db, jwt, ma
├── core/                    código transversal (não é feature de negócio)
│   ├── errors.py            handlers globais de erro padronizados
│   └── auth_decorator.py    helper para extrair user_id do JWT
└── modules/
    ├── users/               cadastro de usuários
    ├── auth/                login e geração de JWT
    ├── records/             medições cardíacas
    └── reports/             relatórios consolidados
```

### Camadas dentro de cada módulo

```
modules/<feature>/
├── routes.py        recebe HTTP, valida via schema, chama service
├── service.py       regras de negócio
├── repository.py    consultas no banco (queries SQLAlchemy)
├── model.py         tabela do banco (classe SQLAlchemy)
└── schemas.py       validação de entrada/saída (Marshmallow)
```

A direção das chamadas é sempre `routes → service → repository → model`.
Schemas são usados em routes (entrada) e service (saída). Não existe
import cruzado entre rotas de módulos diferentes.

### Por que essa estrutura

- **Fronteiras explícitas:** para entender o cadastro de usuário, basta
  abrir `modules/users/`. Tudo está ali
- **Baixo acoplamento:** módulos só conversam por chamadas explícitas
  (ex: `reports` usa `records.repository`)
- **Fácil de explicar na arguição:** a sequência de camadas é a mesma em
  todos os módulos
- **`core/`** guarda o que é transversal (decorator de auth, error
  handlers) e não pertence a nenhuma feature

## Documentação da API

O contrato OpenAPI 3.0 está em [`docs/openapi.yaml`](docs/openapi.yaml).
Pode ser importado direto no Postman, Insomnia ou Swagger Editor.

### Endpoints disponíveis

| Método | Rota         | Auth | Descrição                              |
|--------|--------------|------|------------------------------------------|
| POST   | `/usuarios`  | público | Cadastra um novo usuário              |
| POST   | `/login`     | público | Autentica e devolve token JWT         |

### Autenticação

O login devolve um JWT que deve ser enviado nas próximas requisições no
header:

```
Authorization: Bearer <token>
```

O token expira em **24 horas**. Após esse prazo é preciso fazer login
novamente. Erros de token (ausente, inválido ou expirado) retornam **401**
com mensagem padronizada.

## Como rodar

> Instruções completas serão adicionadas conforme o projeto evolui.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

A API sobe em `http://localhost:3000` e aceita conexões pelo IP da rede
local (necessário para o APK Ionic acessar a API a partir do celular).

## Testes

```bash
pytest                    # roda tudo
pytest -m unit            # apenas testes unitários
pytest -m integration     # apenas testes de integração
```
