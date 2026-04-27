"""
App factory do Flask.

A função `create_app` constrói uma instância do Flask aplicando a configuração
escolhida, inicializando as extensões e registrando os blueprints de cada
módulo. Esse padrão permite criar instâncias diferentes para produção,
desenvolvimento e testes sem duplicar código.

A criação das tabelas (`db.create_all`) é feita apenas em ambiente de
desenvolvimento. Em produção, isso é responsabilidade do `release_command`
do Fly.io, evitando uma race condition entre múltiplos workers do gunicorn
tentarem criar as mesmas tabelas no boot inicial. Em testes, a fixture do
pytest já cria as tabelas explicitamente.
"""

from flask import Flask

from app.config import get_config
from app.core.errors import register_error_handlers
from app.core.health import register_health
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
    register_health(app)

    app.register_blueprint(users_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(records_bp, url_prefix="/api")
    app.register_blueprint(reports_bp, url_prefix="/api")

    if app.config.get("DEBUG"):
        with app.app_context():
            db.create_all()

    return app


def init_database() -> None:
    """
    Cria as tabelas no banco. Usado pelo release_command do Fly.io e por
    quem quiser inicializar o banco manualmente em qualquer ambiente.
    """

    app = create_app()
    with app.app_context():
        db.create_all()
