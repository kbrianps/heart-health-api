"""
Helper de autenticação JWT.

Centraliza a lógica de proteger uma rota e extrair o id do usuário atual
do token JWT. Os módulos de records e reports usam essas funções para
saber qual usuário está fazendo a requisição.

- `jwt_required`: decorator a ser aplicado nas rotas protegidas
- `current_user_id`: retorna o id do usuário autenticado (int)
"""

from flask_jwt_extended import jwt_required as _jwt_required, get_jwt_identity


jwt_required = _jwt_required


def current_user_id() -> int:
    """
    Retorna o id do usuário autenticado a partir do JWT.

    Deve ser chamada dentro de uma rota decorada com `@jwt_required()`.
    O identity é armazenado como string no token (boa prática JWT) e
    convertido para int aqui antes de ser usado nos repositories.
    """

    return int(get_jwt_identity())
