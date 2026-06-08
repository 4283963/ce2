from flask import Blueprint, request, jsonify
from app.services import PaymentService

payment_bp = Blueprint('payment', __name__, url_prefix='/api/payment')


@payment_bp.route('/pay', methods=['POST'])
def pay():
    data = request.get_json()
    if not data:
        return jsonify({
            'code': 400,
            'message': '请求参数不能为空',
            'data': None
        }), 400

    order_id = data.get('order_id')
    pay_method = data.get('pay_method', 'wechat')

    if not order_id:
        return jsonify({
            'code': 400,
            'message': '缺少 order_id 参数',
            'data': None
        }), 400

    result = PaymentService.create_payment(
        order_id=order_id,
        pay_method=pay_method
    )

    if result['success']:
        return jsonify({
            'code': 200,
            'message': result['message'],
            'data': result['data']
        }), 200
    else:
        return jsonify({
            'code': 400,
            'message': result['message'],
            'data': result.get('data')
        }), 400


@payment_bp.route('/transaction/<transaction_no>', methods=['GET'])
def get_transaction(transaction_no):
    result = PaymentService.get_transaction_detail(transaction_no)
    if result['success']:
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': result['data']
        }), 200
    else:
        return jsonify({
            'code': 404,
            'message': result['message'],
            'data': None
        }), 404


@payment_bp.route('/transactions', methods=['GET'])
def list_transactions():
    order_id = request.args.get('order_id')
    if order_id:
        order_id = int(order_id)

    result = PaymentService.list_transactions(order_id=order_id)
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': result['data']
    }), 200
