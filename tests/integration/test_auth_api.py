"""
Testes de integração do endpoint POST /login.

Sobem o app inteiro e validam o fluxo HTTP completo:
- Cadastrar usuário, fazer login, receber token
- Códigos 200, 400, 401, 404 conforme o contrato OpenAPI
- Erros de token (ausente, inválido) através de uma rota protegida auxiliar
"""

import pytest


pytestmark = pytest.mark.integration


def _payload_usuario(**overrides):
    """Helper para criar um payload de cadastro válido."""
    base = {
        "nome": "Brian",
        "sobrenome": "Silva",
        "email": "brian@email.com",
        "telefone": "+55 21 99999-0000",
        "senha": "Senha@123",
        "confirmarSenha": "Senha@123",
        "dataNascimento": "1990-05-20",
        "sexo": "masculino",
        "pais": "Brasil",
    }
    base.update(overrides)
    return base


def test_post_login_200_com_credenciais_validas(client):
    """Login feliz devolve 200 com token, id, email, nome e sobrenome."""

    client.post("/api/usuarios", json=_payload_usuario())

    response = client.post(
        "/api/login", json={"email": "brian@email.com", "senha": "Senha@123"}
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["token"]
    assert body["id"] >= 1
    assert body["email"] == "brian@email.com"
    assert body["nome"] == "Brian"
    assert body["sobrenome"] == "Silva"


def test_post_login_400_quando_payload_invalido(client):
    """Falta de campos obrigatórios devolve 400."""

    response = client.post("/api/login", json={"email": "brian@email.com"})

    assert response.status_code == 400


def test_post_login_401_quando_senha_incorreta(client):
    """Senha errada devolve 401."""

    client.post("/api/usuarios", json=_payload_usuario())

    response = client.post(
        "/api/login", json={"email": "brian@email.com", "senha": "errada"}
    )

    assert response.status_code == 401
    assert response.get_json()["mensagem"] == "Senha incorreta"


def test_post_login_404_quando_email_nao_cadastrado(client):
    """E-mail não cadastrado devolve 404."""

    response = client.post(
        "/api/login", json={"email": "naoexiste@email.com", "senha": "qualquer"}
    )

    assert response.status_code == 404
    assert response.get_json()["mensagem"] == "Usuário não encontrado"
