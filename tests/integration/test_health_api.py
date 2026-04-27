"""
Teste de integração do endpoint de health check.

`/healthz` é um endpoint simples que serve para o Fly.io e monitoring
externo confirmarem que a aplicação está respondendo.
"""

import pytest


pytestmark = pytest.mark.integration


def test_get_healthz_retorna_200_com_status_ok(client):
    """Health check deve responder 200 com status 'ok' e timestamp."""

    response = client.get("/healthz")

    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] == "ok"
    assert body["service"] == "heart-health-api"
    assert "timestamp" in body
