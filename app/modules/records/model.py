"""
Modelo da tabela `records`.

Cada linha representa uma medição cardíaca registrada por um usuário em um
momento específico. A coluna `symptoms` guarda a lista de sintomas como
JSON (suportado nativamente pelo SQLite via SQLAlchemy).
"""

from datetime import datetime, timezone

from app.extensions import db


def _utc_now() -> datetime:
    """Retorna o instante atual em UTC, com timezone preservada."""

    return datetime.now(timezone.utc)


class Record(db.Model):
    """Tabela `records` no banco SQLite."""

    __tablename__ = "records"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    measured_at = db.Column(db.DateTime, default=_utc_now, nullable=False, index=True)

    systolic_pressure = db.Column(db.Integer, nullable=False)
    diastolic_pressure = db.Column(db.Integer, nullable=False)
    heart_rate = db.Column(db.Integer, nullable=False)
    oxygen_saturation = db.Column(db.Integer, nullable=False)
    body_weight = db.Column(db.Float, nullable=False)
    symptoms = db.Column(db.JSON, nullable=False, default=list)

    def __repr__(self) -> str:
        return f"<Record id={self.id} user_id={self.user_id} measured_at={self.measured_at}>"
