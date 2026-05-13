from typing import List, Optional

from app.db import db
from app.models import Security
from app.service.alpha_vantage_client import get_quote


class SecurityException(Exception):
    pass


def get_all_securities() -> List[Security]:
    return db.session.query(Security).all()


def get_security_by_ticker(ticker: str) -> Optional[Security]:
    if not ticker:
        raise SecurityException("Ticker is required")

    quote = get_quote(ticker)
    if quote is None:
        return None

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