"""
Rotas do módulo de registros.

Define o blueprint `records_bp` que expõe:
- POST /registros: registra uma nova medição (autenticada)
- GET /registros: lista as medições do usuário (autenticada)

Ambas exigem token JWT no header `Authorization: Bearer <token>`. O id do
usuário é extraído do token, não do payload, garantindo que ninguém possa
criar ou listar medições de outra pessoa.
"""

from flask import Blueprint, request

from app.core.auth_decorator import current_user_id, jwt_required
from app.modules.records import service
from app.modules.records.schemas import (
    RecordCreateSchema,
    RecordListQuerySchema,
    RecordResponseSchema,
)


records_bp = Blueprint("records", __name__)

_create_schema = RecordCreateSchema()
_response_schema = RecordResponseSchema()
_list_query_schema = RecordListQuerySchema()


@records_bp.post("/registros")
@jwt_required()
def create_record():
    """Registra uma nova medição cardíaca para o usuário autenticado."""

    payload = _create_schema.load(request.get_json() or {})
    record = service.create_record(current_user_id(), payload)
    return _response_schema.dump(service.to_response_dict(record)), 201


@records_bp.get("/registros")
@jwt_required()
def list_records():
    """Lista as medições do usuário autenticado, com filtros opcionais de data."""

    args = _list_query_schema.load(request.args)
    records = service.list_records(
        user_id=current_user_id(),
        date_from=args["date_from"],
        date_to=args["date_to"],
        limit=args["limit"],
    )
    return _response_schema.dump(
        [service.to_response_dict(r) for r in records], many=True
    ), 200
