"""
Rotas do módulo de relatórios.

Define o blueprint `reports_bp` que expõe:
- GET /relatorios?dataInicio=...&dataFim=...: gera o relatório consolidado
  do período para o usuário autenticado

A rota é protegida por JWT. O id do usuário vem do token, garantindo que
ninguém possa gerar relatório dos dados de outra pessoa.
"""

from flask import Blueprint, request

from app.core.auth_decorator import current_user_id, jwt_required
from app.modules.reports import service
from app.modules.reports.schemas import ReportQuerySchema, ReportResponseSchema


reports_bp = Blueprint("reports", __name__)

_query_schema = ReportQuerySchema()
_response_schema = ReportResponseSchema()


@reports_bp.get("/relatorios")
@jwt_required()
def get_report():
    """Gera o relatório consolidado de saúde cardíaca para o período informado."""

    args = _query_schema.load(request.args)
    report = service.build_report(
        user_id=current_user_id(),
        date_from=args["date_from"],
        date_to=args["date_to"],
    )
    return _response_schema.dump(report), 200
