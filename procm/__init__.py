"""procurementManagement (procM) Flask application."""

from __future__ import annotations

from pathlib import Path

from flask import Flask

from procm import config
from procm.db import get_connection, init_db
from procm.api_routes import api_bp
from procm.routes import bp
from procm.seed import seed_business_extensions, seed_if_empty


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.secret_key = config.SECRET_KEY

    if test_config:
        app.config.update(test_config)
        if "DATABASE_PATH" in test_config:
            config.DATABASE_PATH = Path(test_config["DATABASE_PATH"])

    init_db(config.DATABASE_PATH)
    conn = get_connection(config.DATABASE_PATH)
    try:
        seed_if_empty(conn)
        seed_business_extensions(conn)
        conn.commit()
    finally:
        conn.close()

    app.register_blueprint(bp)
    app.register_blueprint(api_bp)
    return app
