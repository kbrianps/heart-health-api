# Imagem base enxuta com Python 3.12
FROM python:3.12-slim

# Variáveis padrão do Python: sem .pyc, log direto no stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    FLASK_ENV=production \
    PORT=8080

WORKDIR /app

# Instala dependências primeiro (camada cacheada enquanto requirements não muda)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY app/ ./app/
COPY docs/ ./docs/
COPY run.py ./

# Diretório onde o SQLite vai morar (montado como volume persistente no Fly)
RUN mkdir -p /data
ENV DATABASE_URL=sqlite:////data/app.db

EXPOSE 8080

# Roda com gunicorn (servidor WSGI de produção, não o dev server do Flask)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--access-logfile", "-", "run:app"]
