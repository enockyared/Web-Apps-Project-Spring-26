from flask import jsonify
from pydantic import ValidationError

from app.db import db

from app.service.portfolio_service import (
    UnsupportedPortfolioOperationError,
    PortfolioOperationError,
)

from app.service.trade_service import (
    TradeExecutionException,
    InsufficientFundsError,
)
from app.service.portfolio_access_service import PortfolioAccessError
from app.service.user_service import UnsupportedUserOperationError
from app.service.security_service import SecurityException


def register_error_handlers(app):

    @app.errorhandler(UnsupportedPortfolioOperationError)
    def handle_unsupported_portfolio_operation(error):
        db.session.rollback()
        return jsonify({
            "error": "Unsupported portfolio operation",
            "detail": str(error)
        }), 400

    @app.errorhandler(PortfolioOperationError)
    def handle_portfolio_operation_error(error):
        db.session.rollback()
        return jsonify({
            "error": "Portfolio operation failed",
            "detail": str(error)
        }), 400

    @app.errorhandler(TradeExecutionException)
    def handle_trade_execution_error(error):
        db.session.rollback()
        return jsonify({
            "error": "Trade execution failed",
            "detail": str(error)
        }), 400

    @app.errorhandler(InsufficientFundsError)
    def handle_insufficient_funds(error):
        db.session.rollback()
        return jsonify({
            "error": "Insufficient funds",
            "detail": str(error)
        }), 400

    @app.errorhandler(UnsupportedUserOperationError)
    def handle_user_error(error):
        db.session.rollback()
        return jsonify({
            "error": "User operation failed",
            "detail": str(error)
        }), 400

    @app.errorhandler(SecurityException)
    def handle_security_error(error):
        db.session.rollback()
        return jsonify({
            "error": "Security operation failed",
            "detail": str(error)
        }), 400

    @app.errorhandler(PortfolioAccessError)
    def handle_portfolio_access_error(error):
        db.session.rollback()
        return jsonify({
            "error": "Portfolio access error",
            "detail": str(error)
        }), 400

    @app.errorhandler(ValueError)
    def handle_value_error(error):
        db.session.rollback()
        return jsonify({
            "error": "External API error",
            "detail": str(error)
        }), 503

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        db.session.rollback()
        return jsonify({
            "error": "Validation error",
            "detail": error.errors()
        }), 422

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        db.session.rollback()
        return jsonify({
            "error": "Internal server error",
            "detail": str(error)
        }), 500