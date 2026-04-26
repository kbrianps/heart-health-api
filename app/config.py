"""
Configurações da aplicação.

Centraliza variáveis de ambiente e valores padrão usados pelo Flask, banco e JWT.
Permite trocar facilmente entre ambientes (desenvolvimento, teste, produção)
sem alterar o código das features.
"""

import os
from datetime import timedelta


class BaseConfig:
    """Configuração base, herdada pelas demais."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-trocar-em-producao-com-pelo-menos-32-bytes")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-trocar-em-producao-com-pelo-menos-32-bytes")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)


class DevelopmentConfig(BaseConfig):
    """Configuração para desenvolvimento local: SQLite em arquivo."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app.db")


class TestingConfig(BaseConfig):
    """Configuração para testes: SQLite em memória, sem persistência."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(BaseConfig):
    """Configuração para produção. Variáveis sensíveis vêm do ambiente."""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")


CONFIG_BY_NAME = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(env_name: str | None = None):
    """Retorna a classe de configuração com base no nome do ambiente."""

    name = env_name or os.getenv("FLASK_ENV", "development")
    return CONFIG_BY_NAME.get(name, DevelopmentConfig)
