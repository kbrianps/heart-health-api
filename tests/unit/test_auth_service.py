"""
Testes unitários do service de autenticação.

Cobrem:
- Login válido devolve um token (string não vazia) e o usuário
- Senha errada lança ApiError 401
- E-mail não cadastrado lança ApiError 404
"""

from datetime import date

import pytest

from app.core.errors import ApiError
from app.modules.auth.service import authenticate
from app.modules.users.service import register_user


pytestmark = pytest.mark.unit


def _registra_usuario():
    """Cadastra um usuário de teste e retorna o objeto criado."""
    return register_user(
        {
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
    )


def test_autentica_com_credenciais_validas(app):
    """Login feliz devolve token JWT e o usuário correspondente."""

    user = _registra_usuario()
    token, returned_user = authenticate("brian@email.com", "Senha@123")

    assert isinstance(token, str) and len(token) > 0
    assert returned_user.id == user.id


def test_falha_quando_senha_incorreta(app):
    """Senha errada lança 401."""

    _registra_usuario()

    with pytest.raises(ApiError) as excinfo:
        authenticate("brian@email.com", "errada")

    assert excinfo.value.codigo == 401


def test_falha_quando_email_nao_cadastrado(app):
    """E-mail desconhecido lança 404."""

    with pytest.raises(ApiError) as excinfo:
        authenticate("naoexiste@email.com", "qualquer")

    assert excinfo.value.codigo == 404
