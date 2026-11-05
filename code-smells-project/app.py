"""Entry point da API da Loja.

Mantém os comandos originais funcionando:
    python app.py
    flask --app app run
"""
from src.app import create_app

app = create_app()

if __name__ == "__main__":
    settings = app.config["SETTINGS"]
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
