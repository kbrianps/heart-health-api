"""
Schemas Marshmallow do módulo de registros.

Os schemas convertem JSON da API (em português, camelCase) para os atributos
internos do modelo (em inglês, snake_case) usando `data_key`. O bloco
`pressaoArterial` é uma estrutura aninhada validada por `PressureSchema`.

- PressureSchema: bloco aninhado com sistolica e diastolica
- RecordCreateSchema: valida o payload de criação (POST /registros)
- RecordResponseSchema: define o JSON de saída
- RecordListQuerySchema: valida query string de filtros do GET /registros
"""

from marshmallow import Schema, fields, validate


class PressureSchema(Schema):
    """Bloco aninhado de pressão arterial (sistólica + diastólica)."""

    systolic = fields.Integer(
        data_key="sistolica",
        required=True,
        validate=validate.Range(min=50, max=250),
    )
    diastolic = fields.Integer(
        data_key="diastolica",
        required=True,
        validate=validate.Range(min=30, max=150),
    )


class RecordCreateSchema(Schema):
    """Valida o payload de criação de uma medição cardíaca."""

    pressure = fields.Nested(
        PressureSchema, data_key="pressaoArterial", required=True
    )
    heart_rate = fields.Integer(
        data_key="frequenciaCardiaca",
        required=True,
        validate=validate.Range(min=30, max=220),
    )
    oxygen_saturation = fields.Integer(
        data_key="oxigenacao",
        required=True,
        validate=validate.Range(min=50, max=100),
    )
    body_weight = fields.Float(
        data_key="pesoCorporal",
        required=True,
        validate=validate.Range(min=20, max=400),
    )
    symptoms = fields.List(
        fields.String(), data_key="sintomas", load_default=list
    )


class RecordResponseSchema(Schema):
    """Define o formato da resposta de uma medição cardíaca."""

    id = fields.Integer()
    measured_at = fields.DateTime(data_key="dataHora")
    pressure = fields.Nested(PressureSchema, data_key="pressaoArterial")
    heart_rate = fields.Integer(data_key="frequenciaCardiaca")
    oxygen_saturation = fields.Integer(data_key="oxigenacao")
    body_weight = fields.Float(data_key="pesoCorporal")
    symptoms = fields.List(fields.String(), data_key="sintomas")


class RecordListQuerySchema(Schema):
    """Valida os parâmetros de query string do GET /registros."""

    date_from = fields.Date(data_key="dataInicio", load_default=None)
    date_to = fields.Date(data_key="dataFim", load_default=None)
    limit = fields.Integer(
        data_key="limite",
        load_default=20,
        validate=validate.Range(min=1, max=100),
    )
