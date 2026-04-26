"""
Rotas do módulo de autenticação.

Define o blueprint `auth_bp` que expõe:
- POST /login: autentica o usuário e devolve um token JWT

A rota apenas recebe o request, valida via schema e delega ao service.
"""

from flask import Blueprint, request

from app.modules.auth.schemas import LoginSchema, LoginResponseSchema
from app.modules.auth.service import authenticate


auth_bp = Blueprint("auth", __name__)

_login_schema = LoginSchema()
_response_schema = LoginResponseSchema()


@auth_bp.post("/login")
def login():
    """Autentica o usuário com e-mail e senha e retorna o token JWT."""

    payload = _login_schema.load(request.get_json() or {})
    token, user = authenticate(payload["email"], payload["password"])
    return _response_schema.dump(
        {
            "token": token,
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "last_name": user.last_name,
        }
    ), 200
