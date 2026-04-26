"""
Testes unitários do service de relatórios.

Cobrem o coração da regra de negócio:
- Período sem registros lança 404
- Datas invertidas lança 400
- Médias são calculadas corretamente para os 5 indicadores
- Sintomas mais frequentes são contabilizados em ordem decrescente
- Alertas são gerados quando há valores fora dos limites de referência
"""

from datetime import date

import pytest

from app.core.errors import ApiError
from app.modules.records.service import create_record
from app.modules.reports.service import build_report
from app.modules.users.service import register_user


pytestmark = pytest.mark.unit


def _registra_usuario():
    """Cadastra um usuário de teste para servir de owner dos registros."""
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


def _medicao(systolic=120, diastolic=80, hr=72, oxygen=98, weight=75.0, symptoms=None):
    """Helper para montar o payload de uma medição."""
    return {
        "pressure": {"systolic": systolic, "diastolic": diastolic},
        "heart_rate": hr,
        "oxygen_saturation": oxygen,
        "body_weight": weight,
        "symptoms": symptoms or [],
    }


def test_lanca_404_quando_periodo_sem_registros(app):
    """Sem nenhum registro do usuário no período, lança 404."""

    user = _registra_usuario()

    with pytest.raises(ApiError) as excinfo:
        build_report(user.id, date(2020, 1, 1), date(2020, 12, 31))

    assert excinfo.value.codigo == 404


def test_lanca_400_quando_periodo_invertido(app):
    """dataInicio posterior a dataFim lança 400."""

    user = _registra_usuario()

    with pytest.raises(ApiError) as excinfo:
        build_report(user.id, date(2030, 1, 1), date(2020, 1, 1))

    assert excinfo.value.codigo == 400


def test_calcula_medias_dos_cinco_indicadores(app):
    """Médias são calculadas corretamente sobre todos os registros do período."""

    user = _registra_usuario()
    create_record(user.id, _medicao(systolic=120, diastolic=80, hr=70, oxygen=98, weight=75.0))
    create_record(user.id, _medicao(systolic=140, diastolic=90, hr=80, oxygen=96, weight=77.0))

    report = build_report(user.id, date(2000, 1, 1), date(2100, 1, 1))

    assert report["averages"]["systolic"] == 130
    assert report["averages"]["diastolic"] == 85
    assert report["averages"]["heart_rate"] == 75
    assert report["averages"]["oxygen"] == 97
    assert report["averages"]["weight"] == 76.0


def test_top_sintomas_em_ordem_decrescente(app):
    """Sintomas mais frequentes vêm primeiro, com no máximo 3 itens."""

    user = _registra_usuario()
    create_record(user.id, _medicao(symptoms=["falta de ar", "tontura"]))
    create_record(user.id, _medicao(symptoms=["falta de ar", "dor no peito"]))
    create_record(user.id, _medicao(symptoms=["falta de ar"]))
    create_record(user.id, _medicao(symptoms=["tontura"]))

    report = build_report(user.id, date(2000, 1, 1), date(2100, 1, 1))

    assert report["top_symptoms"][0] == "falta de ar"
    assert "tontura" in report["top_symptoms"]
    assert len(report["top_symptoms"]) <= 3


def test_gera_alertas_para_valores_acima_dos_limites(app):
    """Alertas mencionam a quantidade de registros fora dos limites."""

    user = _registra_usuario()
    create_record(user.id, _medicao(systolic=145, diastolic=92, hr=110, oxygen=92))
    create_record(user.id, _medicao(systolic=120, diastolic=80, hr=72, oxygen=98))

    report = build_report(user.id, date(2000, 1, 1), date(2100, 1, 1))

    assert any("sistólica" in a.lower() for a in report["alerts"])
    assert any("diastólica" in a.lower() for a in report["alerts"])
    assert any("frequência" in a.lower() for a in report["alerts"])
    assert any("oxigenação" in a.lower() for a in report["alerts"])


def test_sem_alertas_quando_tudo_normal(app):
    """Registros dentro dos limites não geram alertas."""

    user = _registra_usuario()
    create_record(user.id, _medicao(systolic=110, diastolic=70, hr=65, oxygen=98))
    create_record(user.id, _medicao(systolic=115, diastolic=75, hr=70, oxygen=99))

    report = build_report(user.id, date(2000, 1, 1), date(2100, 1, 1))

    assert report["alerts"] == []
