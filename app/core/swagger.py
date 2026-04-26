"""
Configuração do Swagger UI local.

Serve a documentação interativa em `/docs` reaproveitando o mesmo
`docs/openapi.yaml` que é fonte única do contrato.

A função `register_swagger` faz duas coisas:
- Registra o blueprint do flask_swagger_ui em `/docs`
- Adiciona uma rota auxiliar em `/openapi.yaml` que serve o arquivo
  diretamente do diretório `docs/` do projeto
"""

from pathlib import Path

from flask import Flask, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint


SWAGGER_URL = "/docs"
API_SPEC_URL = "/openapi.yaml"

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_DOCS_DIR = _PROJECT_ROOT / "docs"


def register_swagger(app: Flask) -> None:
    """Registra o Swagger UI e a rota que serve o arquivo openapi.yaml."""

    swagger_bp = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_SPEC_URL,
        config={"app_name": "API de Acompanhamento de Saúde Cardíaca"},
    )
    app.register_blueprint(swagger_bp, url_prefix=SWAGGER_URL)

    @app.get(API_SPEC_URL)
    def serve_openapi_spec():
        """Serve o arquivo openapi.yaml para o Swagger UI consumir."""
        return send_from_directory(_DOCS_DIR, "openapi.yaml")
