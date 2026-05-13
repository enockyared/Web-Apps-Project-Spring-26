from typing import Optional

from app.db import db
from app.models import Portfolio, PortfolioAccess


class PortfolioAccessError(Exception):
    pass


VALID_ROLES = {"viewer", "manager"}


def grant_access(portfolio_id: int, username: str, role: str) -> PortfolioAccess:
    if role not in VALID_ROLES:
        raise PortfolioAccessError(f"Invalid role: {role}")

    portfolio = db.session.query(Portfolio).filter_by(id=portfolio_id).one_or_none()
    if portfolio is None:
        raise PortfolioAccessError(f"Portfolio with id {portfolio_id} does not exist.")

    existing = (
        db.session.query(PortfolioAccess)
        .filter_by(portfolio_id=portfolio_id, username=username)
        .one_or_none()
    )

    if existing is not None:
        existing.role = role
        db.session.flush()
        return existing

    access = PortfolioAccess(
        portfolio_id=portfolio_id,
        username=username,
        role=role,
    )
    db.session.add(access)
    db.session.flush()
    return access


def revoke_access(portfolio_id: int, username: str) -> None:
    access = (
        db.session.query(PortfolioAccess)
        .filter_by(portfolio_id=portfolio_id, username=username)
        .one_or_none()
    )

    if access is None:
        raise PortfolioAccessError(
            f"No access grant found for user {username} on portfolio {portfolio_id}."
        )

    db.session.delete(access)
    db.session.flush()


def get_access(portfolio_id: int, username: str) -> Optional[PortfolioAccess]:
    return (
        db.session.query(PortfolioAccess)
        .filter_by(portfolio_id=portfolio_id, username=username)
        .one_or_none()
    )


def is_owner(portfolio: Portfolio, username: str) -> bool:
    return portfolio.owner == username


def can_view_portfolio(portfolio: Portfolio, username: str) -> bool:
    if is_owner(portfolio, username):
        return True

    access = get_access(portfolio.id, username)
    return access is not None and access.role in {"viewer", "manager"}


def can_manage_portfolio(portfolio: Portfolio, username: str) -> bool:
    if is_owner(portfolio, username):
        return True

    access = get_access(portfolio.id, username)
    return access is not None and access.role == "manager"