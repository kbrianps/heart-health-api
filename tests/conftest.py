"""
Fixtures do pytest compartilhadas entre todos os testes.

- `app`: instância do Flask em modo de teste, com banco SQLite em memória
- `client`: cliente HTTP de teste do Flask, usado pelos testes de integração
- `db_session`: sessão do banco resetada a cada teste, evitando que um teste
  influencie outro
"""

import pytest

from app import create_app
from app.extensions import db as _db


@pytest.fixture()
def app():
    """Cria um app Flask isolado, com banco em memória, para cada teste."""

    flask_app = create_app("testing")
    with flask_app.app_context():
        _db.create_all()
        yield flask_app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    """Cliente HTTP de teste para chamar as rotas como se fosse um cliente real."""

    return app.test_client()


@pytest.fixture()
def db_session(app):
    """Expõe a sessão do banco já dentro do contexto do app."""

    return _db.session
