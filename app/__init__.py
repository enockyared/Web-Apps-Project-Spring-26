from flask import Flask

from app.config import get_config
from app.db import db
from app.extensions import cache
from app.routes import portfolio_bp, security_bp, trade_bp, user_bp
from app.errors.handlers import register_error_handlers


def create_app(config=None):
    try:
        if config is None:
            config = get_config(None)

        app = Flask(__name__)
        app.config.from_object(config)

        db.init_app(app)
        cache.init_app(app)

        register_error_handlers(app)

        app.register_blueprint(user_bp, url_prefix="/users")
        app.register_blueprint(portfolio_bp, url_prefix="/portfolios")
        app.register_blueprint(security_bp, url_prefix="/securities")
        app.register_blueprint(trade_bp, url_prefix="/trades")

        return app
    except Exception as e:
        print(f"Error creating app: {e}")
        raise