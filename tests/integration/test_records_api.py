"""
Testes de integração dos endpoints POST /registros e GET /registros.

Sobem o app inteiro com SQLite em memória, autenticam um usuário de teste
e validam todo o fluxo HTTP: códigos de status, formato de resposta,
proteção via JWT e filtros de data.
"""

import pytest


pytestmark = pytest.mark.integration


@pytest.fixture()
def auth_headers(client):
    """
    Fixture que cadastra um usuário, faz login e devolve o header de
    Authorization pronto para uso nos testes de rotas protegidas.
    """

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


def _payload_medicao(**overrides):
    """Helper para montar o payload do request com chaves em português."""
    base = {
        "pressaoArterial": {"sistolica": 120, "diastolica": 80},
        "frequenciaCardiaca": 72,
        "oxigenacao": 98,
        "pesoCorporal": 75.5,
        "sintomas": ["falta de ar", "tontura"],
    }
    base.update(overrides)
    return base


def test_post_registros_201_com_payload_valido(client, auth_headers):
    """Cadastro de medição feliz retorna 201 com a estrutura completa."""

    response = client.post("/api/registros", json=_payload_medicao(), headers=auth_headers)

    assert response.status_code == 201
    body = response.get_json()
    assert body["id"] >= 1
    assert body["pressaoArterial"] == {"sistolica": 120, "diastolica": 80}
    assert body["frequenciaCardiaca"] == 72
    assert body["sintomas"] == ["falta de ar", "tontura"]
    assert "dataHora" in body


def test_post_registros_401_sem_token(client):
    """Sem token JWT retorna 401."""

    response = client.post("/api/registros", json=_payload_medicao())

    assert response.status_code == 401


def test_post_registros_400_quando_valor_fora_do_intervalo(client, auth_headers):
    """Frequência cardíaca fora do range válido retorna 400 com detalhes."""

    response = client.post(
        "/api/registros",
        json=_payload_medicao(frequenciaCardiaca=999),
        headers=auth_headers,
    )

    assert response.status_code == 400
    body = response.get_json()
    assert any("frequenciaCardiaca" in d for d in body.get("detalhes", []))


def test_post_registros_400_quando_pressao_arterial_faltando(client, auth_headers):
    """Bloco pressaoArterial obrigatório ausente retorna 400."""

    payload = _payload_medicao()
    payload.pop("pressaoArterial")

    response = client.post("/api/registros", json=payload, headers=auth_headers)

    assert response.status_code == 400


def test_get_registros_200_lista_vazia(client, auth_headers):
    """Listar sem ter cadastrado nada retorna 200 com array vazio."""

    response = client.get("/api/registros", headers=auth_headers)

    assert response.status_code == 200
    assert response.get_json() == []


def test_get_registros_200_com_registros(client, auth_headers):
    """Após cadastrar medições, GET retorna a lista no formato esperado."""

    client.post("/api/registros", json=_payload_medicao(), headers=auth_headers)
    client.post(
        "/api/registros",
        json=_payload_medicao(frequenciaCardiaca=88),
        headers=auth_headers,
    )

    response = client.get("/api/registros", headers=auth_headers)

    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 2
    assert body[0]["pressaoArterial"]["sistolica"] == 120


def test_get_registros_respeita_limite(client, auth_headers):
    """Parâmetro limite reduz a quantidade retornada."""

    for _ in range(5):
        client.post("/api/registros", json=_payload_medicao(), headers=auth_headers)

    response = client.get("/api/registros?limite=2", headers=auth_headers)

    assert response.status_code == 200
    assert len(response.get_json()) == 2


def test_get_registros_400_quando_periodo_incoerente(client, auth_headers):
    """dataInicio posterior a dataFim retorna 400."""

    response = client.get(
        "/api/registros?dataInicio=2030-01-01&dataFim=2020-01-01",
        headers=auth_headers,
    )

    assert response.status_code == 400
    assert "posterior" in response.get_json()["mensagem"]


def test_get_registros_401_sem_token(client):
    """GET sem token retorna 401."""

    response = client.get("/api/registros")

    assert response.status_code == 401


def test_get_registros_isola_por_usuario(client, auth_headers):
    """
    Cada usuário só vê os próprios registros: cria um registro como Brian,
    cadastra um segundo usuário, faz login e GET dele deve retornar lista vazia.
    """

    client.post("/api/registros", json=_payload_medicao(), headers=auth_headers)

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
        "/api/registros", headers={"Authorization": f"Bearer {other_token}"}
    )

    assert response.status_code == 200
    assert response.get_json() == []
