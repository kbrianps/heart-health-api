# API de Acompanhamento de Saúde Cardíaca

[![CI](https://github.com/kbrianps/heart-health-api/actions/workflows/ci.yml/badge.svg)](https://github.com/kbrianps/heart-health-api/actions/workflows/ci.yml)
[![Deploy](https://github.com/kbrianps/heart-health-api/actions/workflows/deploy.yml/badge.svg)](https://github.com/kbrianps/heart-health-api/actions/workflows/deploy.yml)
[![Sync Postman](https://github.com/kbrianps/heart-health-api/actions/workflows/sync-postman.yml/badge.svg)](https://github.com/kbrianps/heart-health-api/actions/workflows/sync-postman.yml)
[![Run in Postman](https://run.pstmn.io/button.svg)](https://www.postman.com/kbrianps/workspace/heart-health-api/collection/26915556-ac9ad8a1-17e4-41c5-8f37-a93a28e778b3)

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat&logo=sqlite&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat&logo=sqlalchemy&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-Auth-000000?style=flat&logo=jsonwebtokens&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-8.3-0A9EDC?style=flat&logo=pytest&logoColor=white)
![OpenAPI](https://img.shields.io/badge/OpenAPI-3.0-6BA539?style=flat&logo=openapiinitiative&logoColor=white)
![Fly.io](https://img.shields.io/badge/Fly.io-deploy-8B5CF6?style=flat&logo=flydotio&logoColor=white)
![License](https://img.shields.io/badge/license-GPLv3-blue?style=flat)

Backend do Sistema de Acompanhamento de Saúde Cardíaca, desenvolvido como
trabalho da disciplina de **Programação Modular**.

A API permite que usuários se cadastrem, autentiquem-se, registrem medições
cardiovasculares (pressão arterial, frequência cardíaca, oxigenação, peso e
sintomas) e gerem relatórios consolidados por período.

## Equipe

Trabalho desenvolvido pelos seguintes alunos:

- [Brian Kévin dos Santos Pravato](https://github.com/kbrianps)
- [José Henrique de Souza Furtado](https://github.com/furtadoHenrique)
- [Pedro Levi Freitas Nascimento](https://github.com/pedrolevi2003)
- [Natalha da Silva Santanna](https://github.com/NatalhaSantanna)

## Links

- **Repositório:** https://github.com/kbrianps/heart-health-api
- **API em produção:** https://heart-health-api.kbrianps.com (rodando 24/7 no Fly.io)
- **Documentação interativa (Swagger UI):** https://heart-health-api.kbrianps.com/docs
- **URL direta do Fly.io (fallback):** https://heart-health-api.fly.dev
- **Contrato OpenAPI:** [`docs/openapi.yaml`](docs/openapi.yaml)
- **Licença:** [GPL-3.0](LICENSE)

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

A UI interativa do Swagger está disponível em duas URLs e permite testar
todos os endpoints direto do navegador, inclusive os protegidos por JWT
(basta colar o token gerado pelo `/login` no botão **Authorize**):

- **Produção:** https://heart-health-api.kbrianps.com/docs
- **Local:** http://localhost:3000/docs (com a aplicação rodando)

Existe também uma **collection do Postman/Insomnia** pronta:

- [Workspace público no Postman](https://www.postman.com/kbrianps/workspace/heart-health-api)
  com a collection sempre sincronizada com a versão deste repositório
  (sync automático via GitHub Actions a cada commit no JSON da collection)
- [Collection direta no Postman](https://www.postman.com/kbrianps/workspace/heart-health-api/collection/26915556-ac9ad8a1-17e4-41c5-8f37-a93a28e778b3)
- Arquivo local em [`docs/heart-health-api.postman_collection.json`](docs/heart-health-api.postman_collection.json)
  para quem prefere importar manualmente (funciona em Postman e Insomnia)

Faça o login uma vez (o token é salvo automaticamente em uma variável da
collection pelo script de Tests) e dispare os demais requests sem precisar
copiar o token manualmente.

### Endpoints disponíveis

Todos os endpoints da API ficam sob o prefixo `/api`. O `/docs` (Swagger UI)
e o `/openapi.yaml` ficam fora desse prefixo, na raiz do servidor.

| Método | Rota             | Auth | Descrição                              |
|--------|------------------|------|------------------------------------------|
| POST   | `/api/usuarios`  | público | Cadastra um novo usuário              |
| POST   | `/api/login`     | público | Autentica e devolve token JWT         |
| POST   | `/api/registros` | JWT  | Registra uma nova medição cardíaca       |
| GET    | `/api/registros` | JWT  | Lista as medições do usuário             |
| GET    | `/api/relatorios`| JWT  | Gera relatório consolidado por período   |
| GET    | `/docs`          | público | Swagger UI interativo                 |
| GET    | `/openapi.yaml`  | público | Contrato OpenAPI 3.0                  |

**Filtros do GET /registros** (todos opcionais via query string):
- `dataInicio`: data inicial em ISO (`YYYY-MM-DD`)
- `dataFim`: data final em ISO (`YYYY-MM-DD`)
- `limite`: máximo de registros (1 a 100, padrão 20)

**Parâmetros do GET /relatorios** (obrigatórios via query string):
- `dataInicio`: data inicial do período (`YYYY-MM-DD`)
- `dataFim`: data final do período (`YYYY-MM-DD`)

O relatório retorna médias dos 5 indicadores no período, os 3 sintomas
mais frequentes e alertas para valores fora dos limites de referência:

- Pressão sistólica > 130 mmHg
- Pressão diastólica > 85 mmHg
- Frequência cardíaca > 100 bpm
- Oxigenação < 95%

### Autenticação

O login devolve um JWT que deve ser enviado nas próximas requisições no
header:

```
Authorization: Bearer <token>
```

O token expira em **24 horas**. Após esse prazo é preciso fazer login
novamente. Erros de token (ausente, inválido ou expirado) retornam **401**
com mensagem padronizada.

### Exemplos com `curl`

Os exemplos abaixo usam a URL pública. Pra rodar contra o ambiente local,
basta trocar `https://heart-health-api.kbrianps.com` por
`http://localhost:3000`.

**1. Cadastrar usuário**

```bash
curl -X POST https://heart-health-api.kbrianps.com/api/usuarios \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Brian",
    "sobrenome": "Pravato",
    "email": "brian@email.com",
    "telefone": "+55 21 99999-0000",
    "senha": "Senha@123",
    "confirmarSenha": "Senha@123",
    "dataNascimento": "1990-05-20",
    "sexo": "masculino",
    "pais": "Brasil"
  }'
```

**2. Fazer login (salvando o token em variável de shell)**

```bash
TOKEN=$(curl -s -X POST https://heart-health-api.kbrianps.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"brian@email.com","senha":"Senha@123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

echo "$TOKEN"
```

**3. Registrar uma medição cardíaca**

```bash
curl -X POST https://heart-health-api.kbrianps.com/api/registros \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "pressaoArterial": { "sistolica": 120, "diastolica": 80 },
    "frequenciaCardiaca": 72,
    "oxigenacao": 98,
    "pesoCorporal": 75.5,
    "sintomas": ["falta de ar", "tontura"]
  }'
```

**4. Listar medições do usuário**

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "https://heart-health-api.kbrianps.com/api/registros?limite=10"
```

**5. Gerar relatório consolidado de um período**

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "https://heart-health-api.kbrianps.com/api/relatorios?dataInicio=2026-01-01&dataFim=2026-12-31"
```

## Como rodar localmente

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

## Deploy

A API está deployada no [Fly.io](https://fly.io), na região de São Paulo
(`gru`), com SQLite em volume persistente de 1 GB. O subdomínio
`heart-health-api.kbrianps.com` aponta direto para os IPs do Fly via DNS
da Cloudflare.

### Comandos principais

```bash
# Ver logs em tempo real
~/.fly/bin/flyctl logs -a heart-health-api

# Status da máquina
~/.fly/bin/flyctl status -a heart-health-api

# Deploy de uma nova versão (após git push)
~/.fly/bin/flyctl deploy --remote-only

# Setar/atualizar secrets (SECRET_KEY, JWT_SECRET_KEY)
~/.fly/bin/flyctl secrets set CHAVE=valor -a heart-health-api
```

### Estrutura do deploy

- **Imagem Docker** ([`Dockerfile`](Dockerfile)): Python 3.12 slim + gunicorn com 2 workers
- **Configuração Fly** ([`fly.toml`](fly.toml)): app, região, volume, http service e release_command
- **release_command**: roda `init_database()` antes de subir os workers, garantindo
  que as tabelas existam sem race condition entre múltiplos workers
- **Volume persistente**: `heart_health_data` montado em `/data`, onde fica `app.db`
- **Secrets**: `SECRET_KEY` e `JWT_SECRET_KEY` (32 bytes random) gerenciados pelo Fly,
  nunca versionados no git

## CI/CD

O projeto tem pipeline de integração e entrega contínuas via **GitHub Actions**.
Todo push em `main` (ou pull request) dispara automaticamente:

```
push/PR → GitHub
       ↓
  Workflow CI (.github/workflows/ci.yml)
       ↓
   ├── Setup Python 3.12 com cache de pip
   ├── Instala dependências
   ├── Roda testes unitários (pytest -m unit)
   ├── Roda testes de integração (pytest -m integration)
   └── Gera relatório de cobertura
       ↓ (só se tudo passou)
  Workflow Deploy (.github/workflows/deploy.yml)
       ↓
   ├── Setup do flyctl
   ├── flyctl deploy --remote-only
   └── Smoke test em produção (curl /healthz)
       ↓
  ✅ Versão nova rodando em https://heart-health-api.kbrianps.com
```

### Como funciona

- **CI** ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)): garante
  que código quebrado nunca chega à `main`. Roda em todo push e em todo PR
- **CD** ([`.github/workflows/deploy.yml`](.github/workflows/deploy.yml)):
  só dispara depois que o CI passou na `main`. Usa `workflow_run` do
  GitHub Actions, garantindo a sequência. O deploy é remoto (build no
  Fly.io, não na VM do GitHub Actions)
- **Sync Postman** ([`.github/workflows/sync-postman.yml`](.github/workflows/sync-postman.yml)):
  sempre que o JSON da collection muda em main, atualiza automaticamente
  a collection pública via Postman API. Usa filtro de `paths` para só
  rodar quando o arquivo da collection muda, economizando minutos de CI
- **Tokens scoped**: o `FLY_API_TOKEN` é restrito só à app
  `heart-health-api` (gerado com `flyctl tokens create deploy`), e o
  `POSTMAN_API_KEY` só dá acesso à conta do Postman. Mesmo se vazarem,
  o estrago é limitado
- **Smoke test pós-deploy**: depois de subir, o workflow faz um
  `curl /healthz` na URL pública e falha se a aplicação não responder
  200, evitando dar deploy "verde" enquanto a app está caída

### Por que isso ajuda na modularização

Os módulos por feature (`users`, `auth`, `records`, `reports`) permitem
que os testes rodem em paralelo: cada um valida sua área isoladamente,
sem dependência cruzada. Se um módulo quebra, o feedback é imediato e
localizado, sem afetar a confiabilidade dos outros. O pipeline cresce
linearmente com o número de módulos sem desacelerar.

## Roadmap / Próximos passos

Itens previstos para as próximas iterações do projeto, principalmente
quando o frontend Ionic for desenvolvido:

- **Frontend Ionic (Angular ou React)** consumindo esta API, gerando APK
  Android para a entrega da disciplina de front-end
- **Tela de `/admin` no front** com um botão que abre o Swagger UI
  (`https://heart-health-api.kbrianps.com/docs`) em uma nova aba. Útil
  para a equipe inspecionar a API durante o desenvolvimento e nas
  apresentações sem precisar lembrar a URL
- **Cobertura de testes** (`pytest --cov=app`) reportada como badge no
  README
- **Observabilidade**: integração com algum serviço gratuito de logs
  (BetterStack, Logtail) puxando logs do Fly
