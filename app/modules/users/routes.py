"""
Rotas do módulo de usuários.

Define o blueprint `users_bp` que expõe:
- POST /usuarios: cria uma nova conta de usuário

A rota apenas recebe o request, valida o payload via schema e delega ao
service. A resposta também é formatada por um schema, garantindo que o JSON
de saída siga exatamente o contrato OpenAPI.
"""

from flask import Blueprint, request

from app.modules.users.schemas import UserCreateSchema, UserResponseSchema
from app.modules.users.service import register_user


users_bp = Blueprint("users", __name__)

_create_schema = UserCreateSchema()
_response_schema = UserResponseSchema()


@users_bp.post("/usuarios")
def create_user():
    """Cadastra um novo usuário no sistema."""

    payload = _create_schema.load(request.get_json() or {})
    user = register_user(payload)
    return _response_schema.dump(user), 201
