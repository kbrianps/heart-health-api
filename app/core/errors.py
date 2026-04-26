"""
Handlers globais de erro.

Define a `ApiError` (exceção customizada usada pelos services) e registra
handlers no Flask para garantir que toda resposta de erro siga o mesmo
formato JSON definido no contrato OpenAPI:

    {
        "codigo": <int>,
        "mensagem": <str>,
        "detalhes": [<str>, ...]   # opcional
    }
"""

from flask import Flask, jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException


class ApiError(Exception):
    """
    Exceção lançada pelos services quando uma regra de negócio falha.

    Quem captura essa exceção é o handler `handle_api_error`, que transforma
    o conteúdo em uma resposta JSON padronizada.
    """

    def __init__(self, mensagem: str, codigo: int = 400, detalhes: list[str] | None = None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.codigo = codigo
        self.detalhes = detalhes or []


def _build_error_response(codigo: int, mensagem: str, detalhes: list[str] | None = None):
    """Monta o corpo padronizado da resposta de erro."""

    body: dict = {"codigo": codigo, "mensagem": mensagem}
    if detalhes:
        body["detalhes"] = detalhes
    return jsonify(body), codigo


def register_error_handlers(app: Flask) -> None:
    """Registra todos os handlers globais no app Flask."""

    @app.errorhandler(ApiError)
    def handle_api_error(err: ApiError):
        """Erros de regra de negócio lançados pelos services."""
        return _build_error_response(err.codigo, err.mensagem, err.detalhes)

    @app.errorhandler(ValidationError)
    def handle_validation_error(err: ValidationError):
        """Erros do Marshmallow ao validar payloads de entrada."""
        detalhes = []
        for field, msgs in err.messages.items():
            if isinstance(msgs, list):
                for msg in msgs:
                    detalhes.append(f"{field}: {msg}")
            else:
                detalhes.append(f"{field}: {msgs}")
        return _build_error_response(400, "Dados de requisição inválidos", detalhes)

    @app.errorhandler(404)
    def handle_not_found(_err):
        """Rota não encontrada."""
        return _build_error_response(404, "Recurso não encontrado")

    @app.errorhandler(405)
    def handle_method_not_allowed(_err):
        """Método HTTP não permitido na rota."""
        return _build_error_response(405, "Método não permitido")

    @app.errorhandler(HTTPException)
    def handle_http_exception(err: HTTPException):
        """Demais exceções HTTP padrão (mantém o código original)."""
        return _build_error_response(err.code or 500, err.description or "Erro HTTP")

    @app.errorhandler(Exception)
    def handle_unexpected_error(err: Exception):
        """Qualquer outra exceção não tratada vira um 500 padronizado."""
        app.logger.exception("Erro inesperado: %s", err)
        return _build_error_response(500, "Erro interno no servidor")
