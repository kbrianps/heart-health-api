"""
Testes de integração do endpoint POST /usuarios.

Sobem o app inteiro com SQLite em memória e batem na rota como um cliente
HTTP faria. Garantem que o contrato OpenAPI está sendo respeitado:
status codes corretos, formato do JSON de resposta e payload de erro.
"""

import pytest


pytestmark = pytest.mark.integration


def _payload(**overrides):
    """Helper para montar o payload do request com chaves em português."""

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


def test_post_usuarios_201_com_payload_valido(client):
    """Cadastro feliz: retorna 201 e o JSON de resposta no formato do contrato."""

    response = client.post("/api/usuarios", json=_payload())

    assert response.status_code == 201
    body = response.get_json()
    assert body["id"] >= 1
    assert body["nome"] == "Brian"
    assert body["sobrenome"] == "Silva"
    assert body["email"] == "brian@email.com"


def test_post_usuarios_400_quando_campos_obrigatorios_faltando(client):
    """Payload incompleto retorna 400 com lista de detalhes do erro."""

    response = client.post("/api/usuarios", json={"nome": "Brian"})

    assert response.status_code == 400
    body = response.get_json()
    assert body["codigo"] == 400
    assert "detalhes" in body
    assert len(body["detalhes"]) > 0


def test_post_usuarios_400_quando_email_invalido(client):
    """E-mail mal formado retorna 400."""

    response = client.post("/api/usuarios", json=_payload(email="naoeh-email"))

    assert response.status_code == 400
    body = response.get_json()
    assert any("email" in d.lower() for d in body.get("detalhes", []))


def test_post_usuarios_400_quando_senhas_nao_conferem(client):
    """Confirmação de senha diferente retorna 400 com mensagem específica."""

    response = client.post("/api/usuarios", json=_payload(confirmarSenha="Outra@456"))

    assert response.status_code == 400
    body = response.get_json()
    assert "não conferem" in body["mensagem"]


def test_post_usuarios_409_quando_email_ja_cadastrado(client):
    """Cadastrar duas vezes com o mesmo e-mail retorna 409 no segundo POST."""

    client.post("/api/usuarios", json=_payload())
    response = client.post("/api/usuarios", json=_payload())

    assert response.status_code == 409
    body = response.get_json()
    assert body["codigo"] == 409
    assert "já está cadastrado" in body["mensagem"]
