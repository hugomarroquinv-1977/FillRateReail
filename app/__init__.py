"""Paquete de la aplicación FillRateRetail."""

from flask import Flask

from app.controllers import main_bp, ia_bp


def create_app() -> Flask:
    """Crea y configura la aplicación Flask con patrón MVC.

    Returns:
        Flask: Instancia de la aplicación configurada.
    """
    app = Flask(__name__, instance_relative_config=True)

    # Cargar configuración desde .env si existe
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATA_FOLDER="datos",
        FILL_RATE_FOLDER="fill_rate",
        VENTAS_FOLDER="ventas_historicas",
    )

    # Registrar blueprints de controladores
    app.register_blueprint(main_bp)
    app.register_blueprint(ia_bp, url_prefix="/ia")

    @app.after_request
    def evitar_cache(response):
        """Evita que el navegador muestre datos cacheados tras subir un archivo."""
        if response.mimetype == "text/html":
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

    return app
