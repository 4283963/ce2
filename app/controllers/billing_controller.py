from flask import Blueprint, request, jsonify
from app.services import BillingService

billing_bp = Blueprint('billing', __name__, url_prefix='/api/billing')


@billing_bp.route('/calculate', methods=['POST'])
def calculate_fee():
    data = request.get_json()
    if not data:
        return jsonify({
            'code': 400,
            'message': '请求参数不能为空',
            'data': None
        }), 400

    plate_number = data.get('plate_number')
    exit_time = data.get('exit_time')

    if not plate_number:
        return jsonify({
            'code': 400,
            'message': '缺少 plate_number 参数',
            'data': None
        }), 400

    result = BillingService.calculate_parking_fee(
        plate_number=plate_number,
        exit_time=exit_time
    )

    if result['success']:
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': result['data']
        }), 200
    else:
        return jsonify({
            'code': 400,
            'message': result['message'],
            'data': None
        }), 400


@billing_bp.route('/exit', methods=['POST'])
def confirm_exit():
    data = request.get_json()
    if not data:
        return jsonify({
            'code': 400,
            'message': '请求参数不能为空',
            'data': None
        }), 400

    plate_number = data.get('plate_number')
    exit_time = data.get('exit_time')

    if not plate_number:
        return jsonify({
            'code': 400,
            'message': '缺少 plate_number 参数',
            'data': None
        }), 400

    result = BillingService.confirm_exit(
        plate_number=plate_number,
        exit_time=exit_time
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
            'data': None
        }), 400


@billing_bp.route('/order/<order_no>', methods=['GET'])
def get_order(order_no):
    result = BillingService.get_order_detail(order_no)
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


@billing_bp.route('/orders', methods=['GET'])
def list_orders():
    plate_number = request.args.get('plate_number')
    status = request.args.get('status')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))

    result = BillingService.list_orders(
        plate_number=plate_number,
        status=status,
        page=page,
        page_size=page_size
    )

    return jsonify({
        'code': 200,
        'message': 'success',
        'data': result['data'],
        'page': result['page'],
        'page_size': result['page_size']
    }), 200
