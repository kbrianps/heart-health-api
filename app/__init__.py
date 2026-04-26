"""
App factory do Flask.

A função `create_app` constrói uma instância do Flask aplicando a configuração
escolhida, inicializando as extensões e registrando os blueprints de cada
módulo. Esse padrão permite criar instâncias diferentes para produção,
desenvolvimento e testes sem duplicar código.
"""

from flask import Flask

from app.config import get_config
from app.extensions import db, jwt, ma


def create_app(config_name: str | None = None) -> Flask:
    """Cria e configura a instância do Flask, retornando o app pronto para uso."""

    app = Flask(__name__)
    app.config.from_object(get_config(config_name))

    db.init_app(app)
    jwt.init_app(app)
    ma.init_app(app)

    with app.app_context():
        db.create_all()

    return app
