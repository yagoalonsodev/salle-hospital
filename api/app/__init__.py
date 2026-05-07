"""Factory Flask — laSalle Health Center API."""

from flask import Flask

from app.logging_config import setup_logging
from app.routes import (
    dashboard,
    health,
    metrics,
    patients,
    predict,
    sites,
    studies,
    upload,
    web,
)

setup_logging()


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

    app.register_blueprint(web.bp)
    app.register_blueprint(health.bp)
    app.register_blueprint(metrics.bp)
    app.register_blueprint(predict.bp)
    app.register_blueprint(upload.bp)
    app.register_blueprint(patients.bp)
    app.register_blueprint(sites.bp)
    app.register_blueprint(studies.bp)
    app.register_blueprint(dashboard.bp)

    @app.errorhandler(413)
    def too_large(_e):
        return {"error": "Archivo demasiado grande (máx. 10 MB)"}, 413

    return app
