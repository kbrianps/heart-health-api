"""
App factory do Flask.

A função `create_app` constrói uma instância do Flask aplicando a configuração
escolhida, inicializando as extensões e registrando os blueprints de cada
módulo. Esse padrão permite criar instâncias diferentes para produção,
desenvolvimento e testes sem duplicar código.
"""

from flask import Flask

from app.config import get_config
from app.core.errors import register_error_handlers
from app.core.jwt_handlers import register_jwt_handlers
from app.core.swagger import register_swagger
from app.extensions import db, jwt, ma, cors
from app.modules.auth.routes import auth_bp
from app.modules.records.routes import records_bp
from app.modules.reports.routes import reports_bp
from app.modules.users.routes import users_bp


def create_app(config_name: str | None = None) -> Flask:
    """Cria e configura a instância do Flask, retornando o app pronto para uso."""

    app = Flask(__name__)
    app.config.from_object(get_config(config_name))

    db.init_app(app)
    jwt.init_app(app)
    ma.init_app(app)
    cors.init_app(
        app,
        resources={r"/*": {"origins": "*"}},
        supports_credentials=False,
    )

    register_error_handlers(app)
    register_jwt_handlers(jwt)
    register_swagger(app)

    app.register_blueprint(users_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(records_bp)
    app.register_blueprint(reports_bp)

    with app.app_context():
        db.create_all()

    return app
