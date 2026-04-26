"""
Repositório de usuários.

Concentra as consultas SQL ao banco. As regras de negócio ficam no
`service.py`, que chama estas funções. Manter as consultas isoladas aqui
facilita os testes (basta mockar este módulo) e evita espalhar SQL pelo
projeto.
"""

from app.extensions import db
from app.modules.users.model import User


def find_by_email(email: str) -> User | None:
    """Busca um usuário pelo e-mail. Retorna None se não existir."""

    return db.session.query(User).filter_by(email=email).first()


def find_by_id(user_id: int) -> User | None:
    """Busca um usuário pelo id. Retorna None se não existir."""

    return db.session.get(User, user_id)


def create(user: User) -> User:
    """Persiste o usuário no banco e retorna o objeto com o id preenchido."""

    db.session.add(user)
    db.session.commit()
    return user
