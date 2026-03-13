from pydantic import ValidationError

from app.schemas.request_schemas import (
    BuyTradeRequest,
    CreatePortfolioRequest,
    CreateUserRequest,
    SellTradeRequest,
)


def test_create_user_request_valid():
    req = CreateUserRequest(
        username="alice",
        password="password123",
        firstname="Alice",
        lastname="Smith",
        balance=1000.0,
    )

    assert req.username == "alice"
    assert req.balance == 1000.0


def test_create_user_request_missing_fields():
    try:
        CreateUserRequest(
            username="alice",
            password="password123",
            firstname="Alice",
        )
        assert False, "Expected ValidationError"
    except ValidationError as e:
        errors = e.errors()
        fields = [err["loc"][0] for err in errors]
        assert "lastname" in fields
        assert "balance" in fields


def test_create_portfolio_request_valid():
    req = CreatePortfolioRequest(
        username="admin",
        name="Growth",
        description="My growth portfolio",
    )

    assert req.username == "admin"
    assert req.name == "Growth"


def test_buy_trade_request_valid():
    req = BuyTradeRequest(
        ticker="AAPL",
        portfolio_id=1,
        quantity=2,
    )

    assert req.ticker == "AAPL"
    assert req.portfolio_id == 1
    assert req.quantity == 2


def test_buy_trade_request_missing_quantity():
    try:
        BuyTradeRequest(
            ticker="AAPL",
            portfolio_id=1,
        )
        assert False, "Expected ValidationError"
    except ValidationError as e:
        errors = e.errors()
        assert errors[0]["loc"][0] == "quantity"


def test_sell_trade_request_valid():
    req = SellTradeRequest(
        ticker="AAPL",
        portfolio_id=1,
        quantity=2,
        sale_price=150.0,
    )

    assert req.sale_price == 150.0


def test_sell_trade_request_missing_sale_price():
    try:
        SellTradeRequest(
            ticker="AAPL",
            portfolio_id=1,
            quantity=2,
        )
        assert False, "Expected ValidationError"
    except ValidationError as e:
        errors = e.errors()
        assert errors[0]["loc"][0] == "sale_price"