from __future__ import annotations

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.config import TestConfig
from app.db import db
from app.models import Security, User


@pytest.fixture(scope="function")
def app():
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()

        admin_user = User(
            username="admin",
            password="admin",
            firstname="Admin",
            lastname="User",
            balance=10000.00,
        )
        viewer_user = User(
            username="viewer",
            password="viewer",
            firstname="Viewer",
            lastname="User",
            balance=5000.00,
        )
        manager_user = User(
            username="manager",
            password="manager",
            firstname="Manager",
            lastname="User",
            balance=5000.00,
        )

        db.session.add_all([admin_user, viewer_user, manager_user])

        securities = [
            Security(ticker="AAPL", issuer="Apple Inc.", price=150.00),
            Security(ticker="GOOGL", issuer="Alphabet Inc.", price=2800.00),
            Security(ticker="MSFT", issuer="Microsoft Corp.", price=300.00),
        ]
        db.session.add_all(securities)
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


@pytest.fixture(scope="function")
def db_session(app):
    with app.app_context():
        yield db.session