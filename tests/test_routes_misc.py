from unittest.mock import patch

def make_payload(username):
    return {
        "sub": f"{username}-sub",
        "cognito:username": username,
        "username": username,
    }


def test_get_users_route(client):
    with patch("app.auth.auth.validate_token", return_value=make_payload("admin")):
        response = client.get(
            "/users/",
            headers={"Authorization": "Bearer valid"},
        )

    assert response.status_code == 200


def test_get_user_route_not_found(client):
    with patch("app.auth.auth.validate_token", return_value=make_payload("admin")):
        response = client.get(
            "/users/not_real",
            headers={"Authorization": "Bearer valid"},
        )

    assert response.status_code == 404


def test_create_user_route(client):
    with patch("app.auth.auth.validate_token", return_value=make_payload("admin")):
        response = client.post(
            "/users/",
            json={
                "username": "routeuser",
                "password": "pw",
                "firstname": "Route",
                "lastname": "User",
                "balance": 123.0,
            },
            headers={"Authorization": "Bearer valid"},
        )

    assert response.status_code == 201


def test_update_balance_route(client):
    with patch("app.auth.auth.validate_token", return_value=make_payload("admin")):
        response = client.put(
            "/users/update-balance",
            json={"username": "viewer", "new_balance": 777.0},
            headers={"Authorization": "Bearer valid"},
        )

    assert response.status_code == 200


def test_get_security_route(client):
    with patch("app.auth.auth.validate_token", return_value=make_payload("admin")):
        with patch("app.service.security_service.get_quote") as mock_quote:
            mock_quote.return_value = type(
                "Quote",
                (),
                {
                    "ticker": "AAPL",
                    "issuer": "Apple Inc.",
                    "price": 150.0,
                    "date": "2026-03-01",
                },
            )()

            response = client.get(
                "/securities/AAPL",
                headers={"Authorization": "Bearer valid"},
            )

    assert response.status_code == 200


def test_get_security_not_found(client):
    with patch("app.auth.auth.validate_token", return_value=make_payload("admin")):
        with patch("app.service.security_service.get_quote", return_value=None):
            response = client.get(
                "/securities/ZZZZ",
                headers={"Authorization": "Bearer valid"},
            )

    assert response.status_code == 404


    from app.db import db
from app.models import Portfolio, PortfolioAccess, User


def test_get_portfolios_by_user_for_self(client):
    with patch("app.auth.auth.validate_token", return_value=make_payload("admin")):
        response = client.get(
            "/portfolios/user/admin",
            headers={"Authorization": "Bearer valid"},
        )
    assert response.status_code == 200


def test_get_portfolios_by_user_for_other_user_forbidden(client):
    with patch("app.auth.auth.validate_token", return_value=make_payload("viewer")):
        response = client.get(
            "/portfolios/user/admin",
            headers={"Authorization": "Bearer valid"},
        )
    assert response.status_code == 403


def test_create_portfolio_for_self(client):
    with patch("app.auth.auth.validate_token", return_value=make_payload("admin")):
        response = client.post(
            "/portfolios/",
            json={
                "username": "admin",
                "name": "SelfCreate",
                "description": "Created by owner",
            },
            headers={"Authorization": "Bearer valid"},
        )
    assert response.status_code == 201


def test_create_portfolio_for_other_user_forbidden(client):
    with patch("app.auth.auth.validate_token", return_value=make_payload("viewer")):
        response = client.post(
            "/portfolios/",
            json={
                "username": "admin",
                "name": "BadCreate",
                "description": "Should fail",
            },
            headers={"Authorization": "Bearer valid"},
        )
    assert response.status_code == 403


def test_delete_portfolio_owner_only(client, db_session):
    owner = db_session.query(User).filter_by(username="admin").one()
    portfolio = Portfolio(name="DeleteMe", description="D", user=owner)
    db_session.add(portfolio)
    db_session.commit()

    with patch("app.auth.auth.validate_token", return_value=make_payload("viewer")):
        response = client.delete(
            f"/portfolios/{portfolio.id}",
            headers={"Authorization": "Bearer valid"},
        )
    assert response.status_code == 403


def test_delete_portfolio_owner_success(client, db_session):
    owner = db_session.query(User).filter_by(username="admin").one()
    portfolio = Portfolio(name="DeleteSuccess", description="D", user=owner)
    db_session.add(portfolio)
    db_session.commit()

    with patch("app.auth.auth.validate_token", return_value=make_payload("admin")):
        response = client.delete(
            f"/portfolios/{portfolio.id}",
            headers={"Authorization": "Bearer valid"},
        )
    assert response.status_code == 200


def test_get_portfolio_transactions_forbidden_without_access(client, db_session):
    owner = db_session.query(User).filter_by(username="admin").one()
    portfolio = Portfolio(name="TxnForbidden", description="D", user=owner)
    db_session.add(portfolio)
    db_session.commit()

    with patch("app.auth.auth.validate_token", return_value=make_payload("viewer")):
        response = client.get(
            f"/portfolios/{portfolio.id}/transactions",
            headers={"Authorization": "Bearer valid"},
        )
    assert response.status_code == 403


def test_revoke_portfolio_access_success(client, db_session):
    owner = db_session.query(User).filter_by(username="admin").one()
    portfolio = Portfolio(name="RevokeTest", description="D", user=owner)
    db_session.add(portfolio)
    db_session.commit()

    access = PortfolioAccess(portfolio_id=portfolio.id, username="viewer", role="viewer")
    db_session.add(access)
    db_session.commit()

    with patch("app.auth.auth.validate_token", return_value=make_payload("admin")):
        response = client.delete(
            f"/portfolios/{portfolio.id}/access/viewer",
            headers={"Authorization": "Bearer valid"},
        )
    assert response.status_code == 200


def test_revoke_portfolio_access_owner_only(client, db_session):
    owner = db_session.query(User).filter_by(username="admin").one()
    portfolio = Portfolio(name="RevokeForbidden", description="D", user=owner)
    db_session.add(portfolio)
    db_session.commit()

    access = PortfolioAccess(portfolio_id=portfolio.id, username="viewer", role="viewer")
    db_session.add(access)
    db_session.commit()

    with patch("app.auth.auth.validate_token", return_value=make_payload("viewer")):
        response = client.delete(
            f"/portfolios/{portfolio.id}/access/viewer",
            headers={"Authorization": "Bearer valid"},
        )
    assert response.status_code == 403

def test_manager_cannot_create_portfolio(client):
    with patch("app.auth.auth.validate_token", return_value=make_payload("manager_user")):
        response = client.post(
            "/portfolios/",
            json={
                "username": "admin",
                "name": "Illegal Portfolio",
                "description": "Should fail",
            },
            headers={"Authorization": "Bearer valid"},
        )

    assert response.status_code == 403

def test_manager_cannot_delete_portfolio(client, db_session):
    owner = db_session.query(User).filter_by(username="admin").one()
    portfolio = Portfolio(name="MgrDelete", description="D", user=owner)
    db_session.add(portfolio)
    db_session.commit()

    with patch("app.auth.auth.validate_token", return_value=make_payload("manager_user")):
        response = client.delete(
            f"/portfolios/{portfolio.id}",
            headers={"Authorization": "Bearer valid"},
        )

    assert response.status_code == 403

def test_user_without_access_gets_403(client, db_session):
    owner = db_session.query(User).filter_by(username="admin").one()
    portfolio = Portfolio(name="NoAccess", description="D", user=owner)
    db_session.add(portfolio)
    db_session.commit()

    with patch("app.auth.auth.validate_token", return_value=make_payload("random_user")):
        response = client.get(
            f"/portfolios/{portfolio.id}",
            headers={"Authorization": "Bearer valid"},
        )

    assert response.status_code == 403