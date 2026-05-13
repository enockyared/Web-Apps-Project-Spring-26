import pytest
from unittest.mock import patch
from app.service import portfolio_service, user_service
from app.models import Portfolio, Transaction, User
from app.service.trade_service import (
    TradeExecutionException,
    execute_purchase_order,
    liquidate_investment,
    InsufficientFundsError,
)


def create_test_portfolio(db_session):
    admin_user = db_session.query(User).filter_by(username="admin").one()

    portfolio = Portfolio(
        name="Test Portfolio",
        description="Testing trades",
        user=admin_user,
    )

    db_session.add(portfolio)
    db_session.commit()
    return portfolio


def make_quote(ticker="AAPL", issuer="Apple Inc.", price=100.0, date="2026-03-01"):
    return type(
        "Quote",
        (),
        {
            "ticker": ticker,
            "issuer": issuer,
            "price": price,
            "date": date,
        },
    )()


def test_execute_purchase_order_success(db_session):
    portfolio = create_test_portfolio(db_session)

    with patch(
        "app.service.trade_service.get_quote",
        return_value=make_quote(price=100.0),
    ):
        execute_purchase_order(
            portfolio_id=portfolio.id,
            ticker="AAPL",
            quantity=2,
        )

    db_session.flush()
    db_session.refresh(portfolio)

    assert len(portfolio.investments) == 1
    investment = portfolio.investments[0]
    assert investment.ticker == "AAPL"
    assert investment.quantity == 2

    transactions = db_session.query(Transaction).filter_by(portfolio_id=portfolio.id).all()
    assert len(transactions) == 1
    assert transactions[0].transaction_type == "BUY"
    assert transactions[0].ticker == "AAPL"
    assert transactions[0].quantity == 2


def test_execute_purchase_order_insufficient_funds(db_session):
    portfolio = create_test_portfolio(db_session)

    with patch(
        "app.service.trade_service.get_quote",
        return_value=make_quote(price=100000.0),
    ):
        with pytest.raises(InsufficientFundsError):
            execute_purchase_order(
                portfolio_id=portfolio.id,
                ticker="AAPL",
                quantity=10,
            )


def test_liquidate_investment_success(db_session):
    portfolio = create_test_portfolio(db_session)

    with patch(
        "app.service.trade_service.get_quote",
        return_value=make_quote(price=100.0),
    ):
        execute_purchase_order(
            portfolio_id=portfolio.id,
            ticker="AAPL",
            quantity=5,
        )

        liquidate_investment(
            portfolio_id=portfolio.id,
            ticker="AAPL",
            quantity=3,
            sale_price=120.0,
        )

    db_session.flush()
    db_session.refresh(portfolio)

    assert len(portfolio.investments) == 1
    investment = portfolio.investments[0]
    assert investment.quantity == 2

    transactions = db_session.query(Transaction).filter_by(portfolio_id=portfolio.id).all()
    assert len(transactions) == 2
    assert transactions[0].transaction_type == "BUY"
    assert transactions[1].transaction_type == "SELL"


def test_liquidate_investment_insufficient_holdings(db_session):
    portfolio = create_test_portfolio(db_session)

    with patch(
        "app.service.trade_service.get_quote",
        return_value=make_quote(price=100.0),
    ):
        execute_purchase_order(
            portfolio_id=portfolio.id,
            ticker="AAPL",
            quantity=2,
        )

        with pytest.raises(TradeExecutionException):
            liquidate_investment(
                portfolio_id=portfolio.id,
                ticker="AAPL",
                quantity=5,
                sale_price=120.0,
            )


def test_portfolio_service_create_and_delete(db_session):
    admin = user_service.get_user_by_username("admin")
    portfolio_id = portfolio_service.create_portfolio("SvcP", "Desc", admin)
    portfolio = portfolio_service.get_portfolio_by_id(portfolio_id)
    assert portfolio is not None

    portfolio_service.delete_portfolio(portfolio_id)
    assert portfolio_service.get_portfolio_by_id(portfolio_id) is None


def test_user_service_get_all_users(db_session):
    users = user_service.get_all_users()
    assert len(users) >= 3


def test_user_service_update_balance_and_delete(db_session):
    user_service.create_user("tempuser", "pw", "Temp", "User", 100.0)
    user_service.update_user_balance("tempuser", 250.0)
    user = user_service.get_user_by_username("tempuser")
    assert user.balance == 250.0

    user_service.delete_user("tempuser")
    assert user_service.get_user_by_username("tempuser") is None


def test_user_service_delete_admin_raises():
    with pytest.raises(user_service.UnsupportedUserOperationError):
        user_service.delete_user("admin")