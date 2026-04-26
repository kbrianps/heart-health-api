"""
Schemas Marshmallow do módulo de usuários.

Os schemas convertem JSON da API (em português, camelCase) para os atributos
internos do modelo (em inglês, snake_case) usando `data_key`. Eles também
fazem a validação dos campos antes que cheguem ao service.

- UserCreateSchema: valida o payload de criação (POST /usuarios)
- UserResponseSchema: define o JSON retornado ao cliente
"""

from marshmallow import Schema, fields, validate


SEXO_VALORES = ["masculino", "feminino", "outro"]


class UserCreateSchema(Schema):
    """Valida o payload de criação de usuário."""

    name = fields.String(data_key="nome", required=True, validate=validate.Length(min=1, max=100))
    last_name = fields.String(data_key="sobrenome", required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    phone = fields.String(data_key="telefone", required=True, validate=validate.Length(min=5, max=30))
    password = fields.String(data_key="senha", required=True, validate=validate.Length(min=8))
    password_confirmation = fields.String(data_key="confirmarSenha", required=True)
    birth_date = fields.Date(data_key="dataNascimento", required=True)
    gender = fields.String(data_key="sexo", required=True, validate=validate.OneOf(SEXO_VALORES))
    country = fields.String(data_key="pais", required=True, validate=validate.Length(min=1, max=100))


class UserResponseSchema(Schema):
    """Define o formato da resposta de cadastro (e demais retornos do usuário)."""

    id = fields.Integer()
    name = fields.String(data_key="nome")
    last_name = fields.String(data_key="sobrenome")
    email = fields.Email()
