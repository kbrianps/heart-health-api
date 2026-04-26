"""
Schemas Marshmallow do módulo de relatórios.

- ReportQuerySchema: valida os parâmetros obrigatórios de período do GET
- ReportResponseSchema: define o JSON consolidado retornado, com blocos
  aninhados para período, médias, sintomas mais frequentes e alertas
"""

from marshmallow import Schema, fields


class ReportQuerySchema(Schema):
    """Valida a query string do GET /relatorios."""

    date_from = fields.Date(data_key="dataInicio", required=True)
    date_to = fields.Date(data_key="dataFim", required=True)


class PeriodSchema(Schema):
    """Bloco aninhado com a janela de tempo do relatório."""

    start = fields.Date(data_key="inicio")
    end = fields.Date(data_key="fim")


class AveragesSchema(Schema):
    """Bloco aninhado com as médias dos cinco indicadores."""

    systolic = fields.Float(data_key="pressaoSistolica")
    diastolic = fields.Float(data_key="pressaoDiastolica")
    heart_rate = fields.Float(data_key="frequenciaCardiaca")
    oxygen = fields.Float(data_key="oxigenacao")
    weight = fields.Float(data_key="pesoCorporal")


class ReportResponseSchema(Schema):
    """Define o formato da resposta do relatório consolidado."""

    period = fields.Nested(PeriodSchema, data_key="periodo")
    averages = fields.Nested(AveragesSchema, data_key="medias")
    top_symptoms = fields.List(fields.String(), data_key="sintomasMaisFrequentes")
    alerts = fields.List(fields.String(), data_key="alertas")
