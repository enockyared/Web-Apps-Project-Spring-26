from flask import Blueprint, jsonify, request, g

from app.auth.auth import require_auth
import app.service.portfolio_service as portfolio_service
import app.service.transaction_service as transaction_service
import app.service.portfolio_access_service as portfolio_access_service
from app.schemas.request_schemas import CreatePortfolioRequest, GrantPortfolioAccessRequest
import app.service.user_service as user_service
from app.db import db

portfolio_bp = Blueprint('portfolio', __name__)


@portfolio_bp.route('/', methods=['GET'])
@require_auth
def get_all_portfolios():
    portfolios = portfolio_service.get_all_portfolios()
    return jsonify([portfolio.__to_dict__() for portfolio in portfolios]), 200


@portfolio_bp.route('/<int:portfolio_id>', methods=['GET'])
@require_auth
def get_portfolio(portfolio_id):
    portfolio = portfolio_service.get_portfolio_by_id(portfolio_id)
    if portfolio is None:
        return jsonify({'error': f'Portfolio {portfolio_id} not found'}), 404

    if not portfolio_access_service.can_view_portfolio(portfolio, g.username):
        return jsonify({
            'error': 'Forbidden',
            'detail': 'You do not have access to view this portfolio.'
        }), 403

    return jsonify(portfolio.__to_dict__()), 200


@portfolio_bp.route('/user/<username>', methods=['GET'])
@require_auth
def get_portfolios_by_user(username):
    user = user_service.get_user_by_username(username)
    if user is None:
        return jsonify({'error': f'User {username} not found'}), 404

    # users can view their own portfolios list; keep this simple for now
    if g.username != username:
        return jsonify({
            'error': 'Forbidden',
            'detail': 'You do not have access to view this user’s portfolios.'
        }), 403

    portfolios = portfolio_service.get_portfolios_by_user(user)
    return jsonify([portfolio.__to_dict__() for portfolio in portfolios]), 200


@portfolio_bp.route('/', methods=['POST'])
@require_auth
def create_portfolio():
    req_data = CreatePortfolioRequest(**request.get_json())

    if g.username != req_data.username:
        return jsonify({
            'error': 'Forbidden',
            'detail': 'You may only create portfolios for yourself.'
        }), 403

    user = user_service.get_user_by_username(req_data.username)
    if user is None:
        return jsonify({'error': f'User {req_data.username} not found'}), 404

    portfolio_id = portfolio_service.create_portfolio(
        name=req_data.name,
        description=req_data.description,
        user=user,
    )
    db.session.commit()
    return jsonify({'message': 'Portfolio created successfully', 'portfolio_id': portfolio_id}), 201


@portfolio_bp.route('/<int:portfolio_id>', methods=['DELETE'])
@require_auth
def delete_portfolio(portfolio_id):
    portfolio = portfolio_service.get_portfolio_by_id(portfolio_id)
    if portfolio is None:
        return jsonify({'error': f'Portfolio {portfolio_id} not found'}), 404

    if portfolio.owner != g.username:
        return jsonify({
            'error': 'Forbidden',
            'detail': 'Only the portfolio owner can delete this portfolio.'
        }), 403

    portfolio_service.delete_portfolio(portfolio_id)
    db.session.commit()
    return jsonify({'message': 'Portfolio deleted successfully'}), 200


@portfolio_bp.route('/<int:portfolio_id>/transactions', methods=['GET'])
@require_auth
def get_portfolio_transactions(portfolio_id):
    portfolio = portfolio_service.get_portfolio_by_id(portfolio_id)
    if portfolio is None:
        return jsonify({'error': f'Portfolio {portfolio_id} not found'}), 404

    if not portfolio_access_service.can_view_portfolio(portfolio, g.username):
        return jsonify({
            'error': 'Forbidden',
            'detail': 'You do not have access to view this portfolio.'
        }), 403

    transactions = transaction_service.get_transactions_by_portfolio_id(portfolio_id)
    return jsonify([transaction.__to_dict__() for transaction in transactions]), 200


@portfolio_bp.route('/<int:portfolio_id>/access', methods=['POST'])
@require_auth
def grant_portfolio_access(portfolio_id):
    req_data = GrantPortfolioAccessRequest(**request.get_json())

    portfolio = portfolio_service.get_portfolio_by_id(portfolio_id)
    if portfolio is None:
        return jsonify({'error': f'Portfolio {portfolio_id} not found'}), 404

    if portfolio.owner != g.username:
        return jsonify({
            'error': 'Forbidden',
            'detail': 'Only the portfolio owner can grant access.'
        }), 403

    access = portfolio_access_service.grant_access(
        portfolio_id=portfolio_id,
        username=req_data.username,
        role=req_data.role,
    )
    db.session.commit()
    return jsonify({
        'message': 'Portfolio access granted successfully',
        'access': access.__to_dict__()
    }), 201


@portfolio_bp.route('/<int:portfolio_id>/access/<username>', methods=['DELETE'])
@require_auth
def revoke_portfolio_access(portfolio_id, username):
    portfolio = portfolio_service.get_portfolio_by_id(portfolio_id)
    if portfolio is None:
        return jsonify({'error': f'Portfolio {portfolio_id} not found'}), 404

    if portfolio.owner != g.username:
        return jsonify({
            'error': 'Forbidden',
            'detail': 'Only the portfolio owner can revoke access.'
        }), 403

    portfolio_access_service.revoke_access(portfolio_id, username)
    db.session.commit()
    return jsonify({'message': 'Portfolio access revoked successfully'}), 200