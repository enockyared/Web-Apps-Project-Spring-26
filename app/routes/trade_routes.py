from flask import Blueprint, jsonify, request, g

from app.auth.auth import require_auth
from app.db import db
import app.service.portfolio_service as portfolio_service
import app.service.portfolio_access_service as portfolio_access_service
from app.service import trade_service
from app.schemas.request_schemas import BuyTradeRequest, SellTradeRequest

trade_bp = Blueprint('trade', __name__)


@trade_bp.route('/buy', methods=['POST'])
@require_auth
def execute_purchase_order():
    req_data = BuyTradeRequest(**request.get_json())

    portfolio = portfolio_service.get_portfolio_by_id(req_data.portfolio_id)
    if portfolio is None:
        return jsonify({'error': f'Portfolio {req_data.portfolio_id} not found'}), 404

    if not portfolio_access_service.can_manage_portfolio(portfolio, g.username):
        return jsonify({
            'error': 'Forbidden',
            'detail': 'You do not have permission to trade on this portfolio.'
        }), 403

    trade_service.execute_purchase_order(
        portfolio_id=req_data.portfolio_id,
        ticker=req_data.ticker,
        quantity=req_data.quantity,
    )
    db.session.commit()
    return jsonify({'message': 'Purchase order executed successfully'}), 201


@trade_bp.route('/sell', methods=['POST'])
@require_auth
def liquidate_investment():
    req_data = SellTradeRequest(**request.get_json())

    portfolio = portfolio_service.get_portfolio_by_id(req_data.portfolio_id)
    if portfolio is None:
        return jsonify({'error': f'Portfolio {req_data.portfolio_id} not found'}), 404

    if not portfolio_access_service.can_manage_portfolio(portfolio, g.username):
        return jsonify({
            'error': 'Forbidden',
            'detail': 'You do not have permission to trade on this portfolio.'
        }), 403

    trade_service.liquidate_investment(
        portfolio_id=req_data.portfolio_id,
        ticker=req_data.ticker,
        quantity=req_data.quantity,
        sale_price=req_data.sale_price,
    )
    db.session.commit()
    return jsonify({'message': 'Investment liquidated successfully'}), 200