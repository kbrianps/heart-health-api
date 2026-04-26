"""
Schemas Marshmallow do módulo de autenticação.

- LoginSchema: valida o payload do POST /login (email + senha)
- LoginResponseSchema: define o JSON retornado contendo o token JWT e dados
  básicos do usuário autenticado
"""

from marshmallow import Schema, fields, validate


class LoginSchema(Schema):
    """Valida o payload de login."""

    email = fields.Email(required=True)
    password = fields.String(data_key="senha", required=True, validate=validate.Length(min=1))


class LoginResponseSchema(Schema):
    """Define o formato da resposta do login bem-sucedido."""

    token = fields.String()
    id = fields.Integer()
    email = fields.Email()
    name = fields.String(data_key="nome")
    last_name = fields.String(data_key="sobrenome")
