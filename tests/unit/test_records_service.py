"""
Testes unitários do service de registros.

Cobrem:
- Criar medição persiste no banco e devolve o id
- Criar medição com user_id inexistente lança 404
- Listar com data invertida lança 400
- Listar respeita o filtro de datas e o limite
- to_response_dict monta corretamente o bloco aninhado de pressão
"""

from datetime import date, datetime, timedelta, timezone

import pytest

from app.core.errors import ApiError
from app.modules.records.service import (
    create_record,
    list_records,
    to_response_dict,
)
from app.modules.users.service import register_user


pytestmark = pytest.mark.unit


def _registra_usuario(email: str = "brian@email.com"):
    """Cadastra um usuário de teste para servir de owner dos registros."""
    return register_user(
        {
            "name": "Brian",
            "last_name": "Silva",
            "email": email,
            "phone": "+55 21 99999-0000",
            "password": "Senha@123",
            "password_confirmation": "Senha@123",
            "birth_date": date(1990, 5, 20),
            "gender": "masculino",
            "country": "Brasil",
        }
    )


def _payload_medicao(**overrides):
    """Helper para montar payloads válidos com pequenas variações por teste."""
    base = {
        "pressure": {"systolic": 120, "diastolic": 80},
        "heart_rate": 72,
        "oxygen_saturation": 98,
        "body_weight": 75.5,
        "symptoms": ["falta de ar"],
    }
    base.update(overrides)
    return base


def test_cria_registro_e_persiste(app):
    """Criar medição válida grava no banco e atribui id e data_hora."""

    user = _registra_usuario()

    record = create_record(user.id, _payload_medicao())

    assert record.id is not None
    assert record.user_id == user.id
    assert record.systolic_pressure == 120
    assert record.symptoms == ["falta de ar"]


def test_cria_falha_quando_usuario_nao_existe(app):
    """Tentar criar para um user_id inexistente lança 404."""

    with pytest.raises(ApiError) as excinfo:
        create_record(9999, _payload_medicao())

    assert excinfo.value.codigo == 404


def test_lista_com_data_invertida_falha(app):
    """Listar com dataInicio > dataFim lança 400."""

    user = _registra_usuario()

    with pytest.raises(ApiError) as excinfo:
        list_records(user.id, date_from=date(2030, 1, 1), date_to=date(2020, 1, 1))

    assert excinfo.value.codigo == 400


def test_lista_respeita_limite(app):
    """Listar respeita o parâmetro de limite."""

    user = _registra_usuario()
    for _ in range(5):
        create_record(user.id, _payload_medicao())

    records = list_records(user.id, limit=3)

    assert len(records) == 3


def test_to_response_dict_monta_bloco_de_pressao(app):
    """O dicionário de resposta agrupa sistólica e diastólica em um bloco aninhado."""

    user = _registra_usuario()
    record = create_record(user.id, _payload_medicao())

    payload = to_response_dict(record)

    assert payload["pressure"] == {"systolic": 120, "diastolic": 80}
    assert payload["heart_rate"] == 72
    assert payload["symptoms"] == ["falta de ar"]
