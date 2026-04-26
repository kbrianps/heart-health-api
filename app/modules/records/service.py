"""
Service do módulo de registros.

Concentra as regras de negócio:
- create_record: cria uma nova medição para um usuário existente
- list_records: lista medições do usuário com filtros opcionais de data
- to_response_dict: converte um Record em dicionário no formato esperado
  pela resposta JSON (com pressão arterial aninhada)

Erros são lançados como `ApiError` para o handler global formatar.
"""

from datetime import date

from app.core.errors import ApiError
from app.modules.records import repository
from app.modules.records.model import Record
from app.modules.users import repository as users_repository


def create_record(user_id: int, payload: dict) -> Record:
    """
    Cria uma nova medição cardíaca para o usuário autenticado.

    Recebe o payload já validado pelo schema (em snake_case com a pressão
    como bloco aninhado). Retorna o Record persistido com id e data_hora
    preenchidos pelo banco.
    """

    if users_repository.find_by_id(user_id) is None:
        raise ApiError("Usuário não encontrado", codigo=404)

    record = Record(
        user_id=user_id,
        systolic_pressure=payload["pressure"]["systolic"],
        diastolic_pressure=payload["pressure"]["diastolic"],
        heart_rate=payload["heart_rate"],
        oxygen_saturation=payload["oxygen_saturation"],
        body_weight=payload["body_weight"],
        symptoms=payload.get("symptoms") or [],
    )

    return repository.create(record)


def list_records(
    user_id: int,
    date_from: date | None = None,
    date_to: date | None = None,
    limit: int = 20,
) -> list[Record]:
    """
    Lista medições do usuário, do mais recente para o mais antigo.

    Se `date_from` e `date_to` forem informados, valida que o intervalo
    é coerente (início <= fim).
    """

    if date_from and date_to and date_from > date_to:
        raise ApiError("A data final deve ser posterior à data inicial", codigo=400)

    return repository.list_by_user(
        user_id=user_id, date_from=date_from, date_to=date_to, limit=limit
    )


def to_response_dict(record: Record) -> dict:
    """
    Monta o dicionário de resposta de um Record no formato do contrato.

    O schema de resposta espera a pressão como bloco aninhado, mas o modelo
    armazena os valores em colunas separadas. Esta função faz a ponte.
    """

    return {
        "id": record.id,
        "measured_at": record.measured_at,
        "pressure": {
            "systolic": record.systolic_pressure,
            "diastolic": record.diastolic_pressure,
        },
        "heart_rate": record.heart_rate,
        "oxygen_saturation": record.oxygen_saturation,
        "body_weight": record.body_weight,
        "symptoms": record.symptoms or [],
    }
