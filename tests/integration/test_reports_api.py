"""
Testes de integração do endpoint GET /relatorios.

Sobem o app inteiro com SQLite em memória, autenticam um usuário e
validam o fluxo HTTP completo: códigos 200, 400, 401, 404 e o formato
JSON consolidado do relatório.
"""

import pytest


pytestmark = pytest.mark.integration


@pytest.fixture()
def auth_headers(client):
    """Cadastra um usuário, faz login e devolve headers de Authorization."""

    client.post(
        "/api/usuarios",
        json={
            "nome": "Brian",
            "sobrenome": "Silva",
            "email": "brian@email.com",
            "telefone": "+55 21 99999-0000",
            "senha": "Senha@123",
            "confirmarSenha": "Senha@123",
            "dataNascimento": "1990-05-20",
            "sexo": "masculino",
            "pais": "Brasil",
        },
    )
    token = client.post(
        "/api/login", json={"email": "brian@email.com", "senha": "Senha@123"}
    ).get_json()["token"]
    return {"Authorization": f"Bearer {token}"}


def _cria_medicao(client, headers, **overrides):
    """Helper para criar uma medição no banco via POST /registros."""
    payload = {
        "pressaoArterial": {"sistolica": 120, "diastolica": 80},
        "frequenciaCardiaca": 72,
        "oxigenacao": 98,
        "pesoCorporal": 75.5,
        "sintomas": [],
    }
    payload.update(overrides)
    return client.post("/api/registros", json=payload, headers=headers)


def test_get_relatorios_401_sem_token(client):
    """Sem token JWT retorna 401."""

    response = client.get("/api/relatorios?dataInicio=2020-01-01&dataFim=2030-12-31")

    assert response.status_code == 401


def test_get_relatorios_400_sem_parametros(client, auth_headers):
    """Faltando dataInicio e dataFim retorna 400 com detalhes."""

    response = client.get("/api/relatorios", headers=auth_headers)

    assert response.status_code == 400
    body = response.get_json()
    assert "detalhes" in body
    assert any("dataInicio" in d for d in body["detalhes"])
    assert any("dataFim" in d for d in body["detalhes"])


def test_get_relatorios_400_periodo_invertido(client, auth_headers):
    """dataInicio posterior a dataFim retorna 400."""

    response = client.get(
        "/api/relatorios?dataInicio=2030-01-01&dataFim=2020-01-01",
        headers=auth_headers,
    )

    assert response.status_code == 400
    assert "posterior" in response.get_json()["mensagem"]


def test_get_relatorios_404_quando_sem_dados_no_periodo(client, auth_headers):
    """Período sem registros do usuário retorna 404."""

    response = client.get(
        "/api/relatorios?dataInicio=1900-01-01&dataFim=1900-12-31",
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert "Nenhum dado" in response.get_json()["mensagem"]


def test_get_relatorios_200_com_estrutura_completa(client, auth_headers):
    """Relatório retorna 200 com período, médias, sintomas e alertas."""

    _cria_medicao(client, auth_headers)
    _cria_medicao(
        client,
        auth_headers,
        pressaoArterial={"sistolica": 145, "diastolica": 92},
        frequenciaCardiaca=110,
        oxigenacao=92,
        sintomas=["falta de ar", "tontura"],
    )

    response = client.get(
        "/api/relatorios?dataInicio=2020-01-01&dataFim=2030-12-31",
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.get_json()

    assert body["periodo"] == {"inicio": "2020-01-01", "fim": "2030-12-31"}
    assert "pressaoSistolica" in body["medias"]
    assert "pressaoDiastolica" in body["medias"]
    assert "frequenciaCardiaca" in body["medias"]
    assert "oxigenacao" in body["medias"]
    assert "pesoCorporal" in body["medias"]
    assert isinstance(body["sintomasMaisFrequentes"], list)
    assert isinstance(body["alertas"], list)
    assert any("sistólica" in a.lower() for a in body["alertas"])


def test_get_relatorios_isola_por_usuario(client, auth_headers):
    """Relatório de um usuário não enxerga registros de outro."""

    _cria_medicao(client, auth_headers)

    client.post(
        "/api/usuarios",
        json={
            "nome": "Outra",
            "sobrenome": "Pessoa",
            "email": "outra@email.com",
            "telefone": "+55 21 88888-0000",
            "senha": "Senha@123",
            "confirmarSenha": "Senha@123",
            "dataNascimento": "1990-05-20",
            "sexo": "feminino",
            "pais": "Brasil",
        },
    )
    other_token = client.post(
        "/api/login", json={"email": "outra@email.com", "senha": "Senha@123"}
    ).get_json()["token"]

    response = client.get(
        "/api/relatorios?dataInicio=2020-01-01&dataFim=2030-12-31",
        headers={"Authorization": f"Bearer {other_token}"},
    )

    assert response.status_code == 404
