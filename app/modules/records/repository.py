"""
Repositório de registros (medições cardíacas).

Concentra as consultas SQL ao banco. As regras de negócio ficam em
`service.py`. Manter as consultas isoladas aqui facilita os testes e
evita espalhar SQL pelo projeto.
"""

from datetime import date, datetime, time

from app.extensions import db
from app.modules.records.model import Record


def create(record: Record) -> Record:
    """Persiste o registro no banco e retorna o objeto com id preenchido."""

    db.session.add(record)
    db.session.commit()
    return record


def list_by_user(
    user_id: int,
    date_from: date | None = None,
    date_to: date | None = None,
    limit: int = 20,
) -> list[Record]:
    """
    Lista registros de um usuário, do mais recente para o mais antigo.

    Aceita filtros opcionais de data inicial e final (inclusivos). Quando
    `date_to` é informada, considera o dia inteiro (até 23:59:59.999999).
    """

    query = db.session.query(Record).filter(Record.user_id == user_id)

    if date_from is not None:
        start_of_day = datetime.combine(date_from, time.min)
        query = query.filter(Record.measured_at >= start_of_day)

    if date_to is not None:
        end_of_day = datetime.combine(date_to, time.max)
        query = query.filter(Record.measured_at <= end_of_day)

    return query.order_by(Record.measured_at.desc()).limit(limit).all()
