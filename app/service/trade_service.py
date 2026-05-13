import datetime

from app.db import db
from app.models import Investment, Portfolio, Security, Transaction
from app.service.alpha_vantage_client import get_quote


class TradeExecutionException(Exception):
    pass


class InsufficientFundsError(Exception):
    pass


def _get_or_create_security_from_quote(ticker: str) -> Security:
    quote = get_quote(ticker)

    if quote is None:
        raise TradeExecutionException(f"Security with ticker {ticker} does not exist.")

    security = db.session.query(Security).filter_by(ticker=quote.ticker).one_or_none()

    if security is None:
        security = Security(
            ticker=quote.ticker,
            issuer=quote.issuer,
            price=quote.price,
        )
        db.session.add(security)
        db.session.flush()
    else:
        security.issuer = quote.issuer
        security.price = quote.price

    return security


def execute_purchase_order(portfolio_id: int, ticker: str, quantity: int):
    if portfolio_id is None or not ticker or quantity is None or quantity <= 0:
        raise TradeExecutionException(
            f"Invalid purchase order parameters [portfolio_id={portfolio_id}, ticker={ticker}, quantity={quantity}]"
        )

    portfolio = db.session.query(Portfolio).filter_by(id=portfolio_id).one_or_none()
    if not portfolio:
        raise TradeExecutionException(f"Portfolio with id {portfolio_id} does not exist.")

    user = portfolio.user
    if not user:
        raise TradeExecutionException(f"User associated with portfolio {portfolio_id} does not exist.")

    security = _get_or_create_security_from_quote(ticker)

    total_cost = security.price * quantity
    if user.balance < total_cost:
        raise InsufficientFundsError("Insufficient funds to complete the purchase.")

    existing_investment = next((inv for inv in portfolio.investments if inv.ticker == security.ticker), None)
    if existing_investment:
        existing_investment.quantity += quantity
    else:
        portfolio.investments.append(
            Investment(ticker=security.ticker, quantity=quantity, security=security)
        )

    user.balance -= total_cost

    db.session.add(
        Transaction(
            portfolio_id=portfolio.id,
            username=user.username,
            ticker=security.ticker,
            quantity=quantity,
            price=security.price,
            transaction_type="BUY",
            date_time=datetime.datetime.now(),
        )
    )

    db.session.flush()


def liquidate_investment(portfolio_id: int, ticker: str, quantity: int, sale_price: float):
    if portfolio_id is None or not ticker or quantity is None or quantity <= 0:
        raise TradeExecutionException(
            f"Invalid liquidation parameters [portfolio_id={portfolio_id}, ticker={ticker}, quantity={quantity}]"
        )

    if sale_price is None or sale_price < 0:
        raise TradeExecutionException(f"Invalid sale price: {sale_price}")

    portfolio = db.session.query(Portfolio).filter_by(id=portfolio_id).one_or_none()
    if not portfolio:
        raise TradeExecutionException(f"Portfolio with id {portfolio_id} does not exist.")

    user = portfolio.user
    if not user:
        raise TradeExecutionException(f"User associated with portfolio {portfolio_id} does not exist.")

    security = _get_or_create_security_from_quote(ticker)

    investment = next(
        (inv for inv in portfolio.investments if inv.ticker == security.ticker),
        None,
    )
    if not investment:
        raise TradeExecutionException(
            f"No investment with ticker {ticker} exists in portfolio with id {portfolio_id}"
        )

    if investment.quantity < quantity:
        raise TradeExecutionException(
            f"Cannot liquidate {quantity} shares of {ticker}. Only {investment.quantity} shares available in portfolio."
        )

    total_proceeds = sale_price * quantity
    user.balance += total_proceeds

    if investment.quantity == quantity:
        db.session.delete(investment)
    else:
        investment.quantity -= quantity

    db.session.add(
        Transaction(
            portfolio_id=portfolio.id,
            username=user.username,
            ticker=security.ticker,
            quantity=quantity,
            price=sale_price,
            transaction_type="SELL",
            date_time=datetime.datetime.now(),
        )
    )

    db.session.flush()