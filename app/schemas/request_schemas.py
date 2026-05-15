from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    username: str
    password: str
    firstname: str
    lastname: str
    balance: float


class CreatePortfolioRequest(BaseModel):
    username: str
    name: str
    description: str


class BuyTradeRequest(BaseModel):
    ticker: str
    portfolio_id: int
    quantity: float


class SellTradeRequest(BaseModel):
    portfolio_id: int
    ticker: str
    quantity: int
    sale_price: float


class GrantPortfolioAccessRequest(BaseModel):
    username: str
    role: str