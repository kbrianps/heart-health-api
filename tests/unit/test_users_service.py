"""
Testes unitários do service de usuários.

Esses testes exercitam apenas a função `register_user`, isoladamente, mas
ainda usando o banco em memória (mais simples do que mockar o repository).

Cobrem:
- Cadastro válido cria usuário com senha hashada (e nunca em texto puro)
- Senhas diferentes resultam em ApiError 400
- E-mail duplicado resulta em ApiError 409
"""

from datetime import date

import pytest

from app.core.errors import ApiError
from app.modules.users.service import register_user


pytestmark = pytest.mark.unit


def _payload(**overrides):
    """Helper para montar payloads válidos com pequenas variações por teste."""

    base = {
        "name": "Brian",
        "last_name": "Silva",
        "email": "brian@email.com",
        "phone": "+55 21 99999-0000",
        "password": "Senha@123",
        "password_confirmation": "Senha@123",
        "birth_date": date(1990, 5, 20),
        "gender": "masculino",
        "country": "Brasil",
    }
    base.update(overrides)
    return base


def test_registra_usuario_com_dados_validos(app):
    """Cadastro feliz: persiste no banco e gera hash diferente da senha original."""

    user = register_user(_payload())

    assert user.id is not None
    assert user.email == "brian@email.com"
    assert user.password_hash != "Senha@123"


def test_falha_quando_senhas_nao_conferem(app):
    """Confirmação de senha diferente deve lançar 400."""

    with pytest.raises(ApiError) as excinfo:
        register_user(_payload(password_confirmation="Outra@456"))

    assert excinfo.value.codigo == 400
    assert "não conferem" in excinfo.value.mensagem


def test_falha_quando_email_ja_cadastrado(app):
    """Tentar cadastrar com e-mail já existente deve lançar 409."""

    register_user(_payload())

    with pytest.raises(ApiError) as excinfo:
        register_user(_payload(email="brian@email.com"))

    assert excinfo.value.codigo == 409
