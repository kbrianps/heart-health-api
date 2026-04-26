"""
Instâncias compartilhadas das extensões do Flask.

São criadas aqui de forma global, mas só inicializadas (com `init_app`)
dentro do app factory em `__init__.py`. Esse padrão evita import circular
entre os módulos e permite reusar as mesmas instâncias em testes.

Extensões registradas:
- db: SQLAlchemy (ORM)
- jwt: gerenciador de tokens JWT
- ma: Marshmallow (validação e serialização)
- cors: liberação de requisições cross-origin (necessário para o app Ionic
  consumir a API a partir do celular Android)
"""

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_cors import CORS

db = SQLAlchemy()
jwt = JWTManager()
ma = Marshmallow()
cors = CORS()
