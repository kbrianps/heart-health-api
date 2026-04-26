"""
Ponto de entrada para rodar o app em desenvolvimento.

Executa: `python run.py`

O host `0.0.0.0` permite acesso pelo IP da máquina na rede local, o que é
necessário para o APK Ionic conseguir consumir a API a partir do celular.
"""

from app import create_app

app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
