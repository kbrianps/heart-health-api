"""
Handlers do Flask-JWT-Extended.

Personalizam as respostas JSON quando o token JWT está ausente, inválido
ou expirado, mantendo o mesmo formato de erro do contrato OpenAPI:

    { "codigo": 401, "mensagem": "..." }
"""

from flask import jsonify
from flask_jwt_extended import JWTManager


def _resposta_nao_autorizado(mensagem: str):
    """Monta o body padronizado de erro 401."""
    return jsonify({"codigo": 401, "mensagem": mensagem}), 401


def register_jwt_handlers(jwt: JWTManager) -> None:
    """Registra os callbacks do JWTManager."""

    @jwt.unauthorized_loader
    def _missing_token(_reason: str):
        return _resposta_nao_autorizado("Token de autenticação ausente")

    @jwt.invalid_token_loader
    def _invalid_token(_reason: str):
        return _resposta_nao_autorizado("Token inválido")

    @jwt.expired_token_loader
    def _expired_token(_jwt_header, _jwt_payload):
        return _resposta_nao_autorizado("Token expirado, faça login novamente")
