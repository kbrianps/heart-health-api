"""
Service do módulo de autenticação.

Concentra a regra de login:
- Procura o usuário pelo e-mail
- Confere a senha contra o hash armazenado
- Gera um token JWT contendo o id do usuário (subject)

Erros são lançados como `ApiError` para que o handler global formate a
resposta JSON conforme o contrato OpenAPI.
"""

from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash

from app.core.errors import ApiError
from app.modules.users import repository as users_repository
from app.modules.users.model import User


def authenticate(email: str, password: str) -> tuple[str, User]:
    """
    Autentica o usuário e gera um token JWT.

    Retorna uma tupla (token, user). Lança ApiError 404 se o e-mail não
    existir e ApiError 401 se a senha estiver incorreta.
    """

    user = users_repository.find_by_email(email)
    if user is None:
        raise ApiError("Usuário não encontrado", codigo=404)

    if not check_password_hash(user.password_hash, password):
        raise ApiError("Senha incorreta", codigo=401)

    token = create_access_token(identity=str(user.id))
    return token, user
