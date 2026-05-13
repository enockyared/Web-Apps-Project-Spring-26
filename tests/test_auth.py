from unittest.mock import patch

from app.db import db
from app.models import Portfolio, PortfolioAccess, User
import pytest
import jwt
from app.auth.auth import AuthError, _extract_bearer_token


def make_payload(username):
    return {
        "sub": f"{username}-sub",
        "cognito:username": username,
        "username": username,
    }


def ensure_portfolio(db_session, owner_username="admin"):
    owner = db_session.query(User).filter_by(username=owner_username).one()
    portfolio = Portfolio(
        name="Authz Portfolio",
        description="Authorization testing",
        user=owner,
    )
    db_session.add(portfolio)
    db_session.commit()
    return portfolio


def test_owner_can_view_portfolio(client, db_session):
    portfolio = ensure_portfolio(db_session, "admin")

    with patch("app.auth.auth.validate_token", return_value=make_payload("admin")):
        response = client.get(
            f"/portfolios/{portfolio.id}",
            headers={"Authorization": "Bearer valid"},
        )

    assert response.status_code == 200


def test_user_without_access_cannot_view_portfolio(client, db_session):
    portfolio = ensure_portfolio(db_session, "admin")

    with patch("app.auth.auth.validate_token", return_value=make_payload("viewer")):
        response = client.get(
            f"/portfolios/{portfolio.id}",
            headers={"Authorization": "Bearer valid"},
        )

    assert response.status_code == 403


def test_owner_can_grant_viewer_access(client, db_session):
    portfolio = ensure_portfolio(db_session, "admin")

    with patch("app.auth.auth.validate_token", return_value=make_payload("admin")):
        response = client.post(
            f"/portfolios/{portfolio.id}/access",
            json={"username": "viewer", "role": "viewer"},
            headers={"Authorization": "Bearer valid"},
        )

    assert response.status_code == 201
    data = response.get_json()
    assert data["access"]["role"] == "viewer"


def test_viewer_can_view_but_cannot_trade(client, db_session):
    portfolio = ensure_portfolio(db_session, "admin")

    access = PortfolioAccess(
        portfolio_id=portfolio.id,
        username="viewer",
        role="viewer",
    )
    db_session.add(access)
    db_session.commit()

    with patch("app.auth.auth.validate_token", return_value=make_payload("viewer")):
        view_response = client.get(
            f"/portfolios/{portfolio.id}",
            headers={"Authorization": "Bearer valid"},
        )
        trade_response = client.post(
            "/trades/buy",
            json={"ticker": "AAPL", "portfolio_id": portfolio.id, "quantity": 1},
            headers={"Authorization": "Bearer valid"},
        )

    assert view_response.status_code == 200
    assert trade_response.status_code == 403


def test_manager_can_trade(client, db_session):
    portfolio = ensure_portfolio(db_session, "admin")

    access = PortfolioAccess(
        portfolio_id=portfolio.id,
        username="manager",
        role="manager",
    )
    db_session.add(access)
    db_session.commit()

    with patch("app.auth.auth.validate_token", return_value=make_payload("manager")):
        with patch("app.service.trade_service.get_quote") as mock_quote:
            mock_quote.return_value = type(
                "Quote",
                (),
                {
                    "ticker": "AAPL",
                    "issuer": "Apple Inc.",
                    "price": 100.0,
                    "date": "2026-03-01",
                },
            )()

            response = client.post(
                "/trades/buy",
                json={"ticker": "AAPL", "portfolio_id": portfolio.id, "quantity": 1},
                headers={"Authorization": "Bearer valid"},
            )

    assert response.status_code in (200, 201)


def test_only_owner_can_revoke_access(client, db_session):
    portfolio = ensure_portfolio(db_session, "admin")

    access = PortfolioAccess(
        portfolio_id=portfolio.id,
        username="viewer",
        role="viewer",
    )
    db_session.add(access)
    db_session.commit()

    with patch("app.auth.auth.validate_token", return_value=make_payload("viewer")):
        response = client.delete(
            f"/portfolios/{portfolio.id}/access/viewer",
            headers={"Authorization": "Bearer valid"},
        )

    assert response.status_code == 403


def test_extract_bearer_token_missing_header(app):
    with app.test_request_context("/users/"):
        with pytest.raises(AuthError):
            _extract_bearer_token()


def test_extract_bearer_token_bad_format(app):
    with app.test_request_context("/users/", headers={"Authorization": "Bad token"}):
        with pytest.raises(AuthError):
            _extract_bearer_token()

def test_protected_route_expired_token(client):

    with patch(
        "app.auth.auth.validate_token",
        side_effect=Exception("Token expired"),
    ):
        response = client.get(
            "/users/",
            headers={"Authorization": "Bearer expiredtoken"},
        )

    assert response.status_code == 403