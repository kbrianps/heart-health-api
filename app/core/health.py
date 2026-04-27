"""
Endpoint de health check.

Expõe `/healthz` na raiz do servidor (fora do prefixo `/api`) seguindo a
convenção cloud-native (Kubernetes, Google, etc) de usar `healthz` para
indicar saúde da aplicação.

Retorna 200 com um pequeno JSON contendo status e timestamp UTC. Pode ser
usado por monitoring externo (UptimeRobot, Cloudflare Health Checks, etc)
ou pelo próprio Fly.io para checagens de liveness.
"""

from datetime import datetime, timezone

from flask import Blueprint, Flask, jsonify


health_bp = Blueprint("health", __name__)


@health_bp.get("/healthz")
def healthz():
    """Indica que a aplicação está de pé respondendo a requisições."""

    return jsonify(
        {
            "status": "ok",
            "service": "heart-health-api",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )


def register_health(app: Flask) -> None:
    """Registra o blueprint de health check no app."""

    app.register_blueprint(health_bp)
