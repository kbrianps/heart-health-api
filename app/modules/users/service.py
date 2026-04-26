"""
Service do módulo de usuários.

Concentra as regras de negócio do cadastro:
- Verifica se a confirmação da senha bate com a senha
- Verifica se o e-mail já está em uso
- Gera o hash da senha (nunca salva texto puro no banco)
- Persiste e retorna o usuário criado

Erros são lançados como `ApiError` e capturados pelo handler global, que
formata a resposta JSON de acordo com o contrato OpenAPI.
"""

from werkzeug.security import generate_password_hash

from app.core.errors import ApiError
from app.modules.users import repository
from app.modules.users.model import User


def register_user(payload: dict) -> User:
    """
    Cria um novo usuário a partir do payload já validado pelo schema.

    Recebe um dicionário com chaves em snake_case (já mapeadas pelo schema).
    Retorna o objeto User persistido com id preenchido.
    """

    if payload["password"] != payload["password_confirmation"]:
        raise ApiError("As senhas informadas não conferem", codigo=400)

    if repository.find_by_email(payload["email"]) is not None:
        raise ApiError("O e-mail informado já está cadastrado", codigo=409)

    user = User(
        name=payload["name"],
        last_name=payload["last_name"],
        email=payload["email"],
        phone=payload["phone"],
        password_hash=generate_password_hash(payload["password"]),
        birth_date=payload["birth_date"],
        gender=payload["gender"],
        country=payload["country"],
    )

    return repository.create(user)
