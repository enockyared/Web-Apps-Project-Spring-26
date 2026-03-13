from unittest.mock import patch

from app.db import db
from app.models import Portfolio, User
from app.service.portfolio_access_service import PortfolioAccessError
from app.service.portfolio_service import PortfolioOperationError
from app.service.security_service import SecurityException
from app.service.trade_service import InsufficientFundsError, TradeExecutionException
from app.service.user_service import UnsupportedUserOperationError


def make_payload(username):
    return {
        "sub": f"{username}-sub",
        "cognito:username": username,
        "username": username,
    }


def make_portfolio(db_session, owner_username="admin"):
    owner = db_session.query(User).filter_by(username=owner_username).one()
    portfolio = Portfolio(name="ErrTradePortfolio", description="D", user=owner)
    db_session.add(portfolio)
    db_session.commit()
    return portfolio


def test_trade_execution_error_handler(client, db_session):
    portfolio = make_portfolio(db_session)

    with patch("app.auth.auth.validate_token", return_value=make_payload("admin")):
        with patch(
            "app.routes.trade_routes.trade_service.execute_purchase_order",
            side_effect=TradeExecutionException("boom"),
        ):
            response = client.post(
                "/trades/buy",
                json={"ticker": "AAPL", "portfolio_id": portfolio.id, "quantity": 1},
                headers={"Authorization": "Bearer valid"},
            )

    assert response.status_code == 400


def test_insufficient_funds_error_handler(client, db_session):
    portfolio = make_portfolio(db_session)

    with patch("app.auth.auth.validate_token", return_value=make_payload("admin")):
        with patch(
            "app.routes.trade_routes.trade_service.execute_purchase_order",
            side_effect=InsufficientFundsError("not enough"),
        ):
            response = client.post(
                "/trades/buy",
                json={"ticker": "AAPL", "portfolio_id": portfolio.id, "quantity": 1},
                headers={"Authorization": "Bearer valid"},
            )

    assert response.status_code == 400


def test_user_error_handler(client):
    with patch("app.auth.auth.validate_token", return_value=make_payload("admin")):
        with patch(
            "app.routes.user_routes.user_service.get_all_users",
            side_effect=UnsupportedUserOperationError("bad user op"),
        ):
            response = client.get(
                "/users/",
                headers={"Authorization": "Bearer valid"},
            )

    assert response.status_code == 400


def test_security_error_handler(client):
    with patch("app.auth.auth.validate_token", return_value=make_payload("admin")):
        with patch(
            "app.routes.security_routes.security_service.get_all_securities",
            side_effect=SecurityException("bad security op"),
        ):
            response = client.get(
                "/securities/",
                headers={"Authorization": "Bearer valid"},
            )

    assert response.status_code == 400


def test_portfolio_access_error_handler(client, db_session):
    portfolio = make_portfolio(db_session)

    with patch("app.auth.auth.validate_token", return_value=make_payload("admin")):
        with patch(
            "app.routes.portfolio_routes.portfolio_access_service.grant_access",
            side_effect=PortfolioAccessError("bad access op"),
        ):
            response = client.post(
                f"/portfolios/{portfolio.id}/access",
                json={"username": "viewer", "role": "viewer"},
                headers={"Authorization": "Bearer valid"},
            )

    assert response.status_code == 400


def test_validation_error_handler_route(client):
    with patch("app.auth.auth.validate_token", return_value=make_payload("admin")):
        response = client.post(
            "/users/",
            json={
                "username": "baduser",
                "password": "pw",
                "firstname": "Bad"
            },
            headers={"Authorization": "Bearer valid"},
        )

    assert response.status_code == 422