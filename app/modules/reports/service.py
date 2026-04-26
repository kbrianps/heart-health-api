"""
Service do módulo de relatórios.

Concentra a regra de geração do relatório consolidado:
- Valida o intervalo (início <= fim)
- Busca os registros do período via `records.repository`
- Calcula médias dos 5 indicadores
- Conta os 3 sintomas mais frequentes
- Gera alertas para valores fora dos limites de referência clínica

Os limites usados nos alertas são valores de referência simples adotados
para fins acadêmicos. Em produção, a análise clínica deveria ser feita
por um especialista.

Erros são lançados como `ApiError` para o handler global formatar.
"""

from collections import Counter
from datetime import date

from app.core.errors import ApiError
from app.modules.records import repository as records_repository
from app.modules.records.model import Record


SYSTOLIC_THRESHOLD = 130
DIASTOLIC_THRESHOLD = 85
OXYGEN_MIN_THRESHOLD = 95
HEART_RATE_THRESHOLD = 100

_MAX_RECORDS_FOR_REPORT = 10_000


def build_report(user_id: int, date_from: date, date_to: date) -> dict:
    """
    Monta o relatório consolidado de saúde cardíaca de um usuário.

    Lança 400 se o intervalo for incoerente, 404 se não houver registros
    no período. Retorna um dicionário no formato esperado pelo schema de
    resposta (chaves em snake_case, mapeadas para camelCase pelo schema).
    """

    if date_from > date_to:
        raise ApiError("A data final deve ser posterior à data inicial", codigo=400)

    records = records_repository.list_by_user(
        user_id=user_id,
        date_from=date_from,
        date_to=date_to,
        limit=_MAX_RECORDS_FOR_REPORT,
    )

    if not records:
        raise ApiError("Nenhum dado encontrado para o período informado", codigo=404)

    return {
        "period": {"start": date_from, "end": date_to},
        "averages": _compute_averages(records),
        "top_symptoms": _top_symptoms(records, top_n=3),
        "alerts": _build_alerts(records),
    }


def _compute_averages(records: list[Record]) -> dict:
    """Calcula a média dos 5 indicadores principais."""

    n = len(records)
    return {
        "systolic": round(sum(r.systolic_pressure for r in records) / n),
        "diastolic": round(sum(r.diastolic_pressure for r in records) / n),
        "heart_rate": round(sum(r.heart_rate for r in records) / n),
        "oxygen": round(sum(r.oxygen_saturation for r in records) / n),
        "weight": round(sum(r.body_weight for r in records) / n, 1),
    }


def _top_symptoms(records: list[Record], top_n: int) -> list[str]:
    """Retorna os sintomas mais reportados em ordem decrescente de frequência."""

    all_symptoms: list[str] = []
    for record in records:
        all_symptoms.extend(record.symptoms or [])
    return [symptom for symptom, _ in Counter(all_symptoms).most_common(top_n)]


def _build_alerts(records: list[Record]) -> list[str]:
    """Gera mensagens de alerta para indicadores fora dos limites clínicos."""

    alerts: list[str] = []

    high_systolic = sum(1 for r in records if r.systolic_pressure > SYSTOLIC_THRESHOLD)
    if high_systolic:
        alerts.append(f"Pressão sistólica acima do ideal em {high_systolic} registros")

    high_diastolic = sum(1 for r in records if r.diastolic_pressure > DIASTOLIC_THRESHOLD)
    if high_diastolic:
        alerts.append(f"Pressão diastólica acima do ideal em {high_diastolic} registros")

    low_oxygen = sum(1 for r in records if r.oxygen_saturation < OXYGEN_MIN_THRESHOLD)
    if low_oxygen:
        alerts.append(f"Oxigenação abaixo do ideal em {low_oxygen} registros")

    high_heart_rate = sum(1 for r in records if r.heart_rate > HEART_RATE_THRESHOLD)
    if high_heart_rate:
        alerts.append(f"Frequência cardíaca elevada em {high_heart_rate} registros")

    return alerts
