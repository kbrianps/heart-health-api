"""
Instâncias compartilhadas das extensões do Flask.

São criadas aqui de forma global, mas só inicializadas (com `init_app`)
dentro do app factory em `__init__.py`. Esse padrão evita import circular
entre os módulos e permite reusar as mesmas instâncias em testes.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
jwt = JWTManager()
ma = Marshmallow()
