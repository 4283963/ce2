from flask import Blueprint, request, jsonify
from app.services import PropertyBillService

property_bill_bp = Blueprint('property_bill', __name__, url_prefix='/api/property-bill')


@property_bill_bp.route('/list', methods=['GET'])
def list_bills():
    plate_number = request.args.get('plate_number')
    status = request.args.get('status')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))

    result = PropertyBillService.list_bills(
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


@property_bill_bp.route('/<int:bill_id>', methods=['GET'])
def get_bill(bill_id):
    result = PropertyBillService.get_bill_detail(bill_id)
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


@property_bill_bp.route('/no/<bill_no>', methods=['GET'])
def get_bill_by_no(bill_no):
    result = PropertyBillService.get_bill_by_no(bill_no)
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


@property_bill_bp.route('', methods=['POST'])
def create_bill():
    data = request.get_json()
    if not data:
        return jsonify({
            'code': 400,
            'message': '请求参数不能为空',
            'data': None
        }), 400

    plate_number = data.get('plate_number')
    bill_month = data.get('bill_month')
    total_amount = data.get('total_amount')
    owner_name = data.get('owner_name')
    due_date = data.get('due_date')

    if not plate_number or not bill_month or total_amount is None:
        return jsonify({
            'code': 400,
            'message': '缺少必要参数',
            'data': None
        }), 400

    result = PropertyBillService.create_bill(
        plate_number=plate_number,
        bill_month=bill_month,
        total_amount=float(total_amount),
        owner_name=owner_name,
        due_date=due_date
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


@property_bill_bp.route('/<int:bill_id>', methods=['PUT'])
def update_bill(bill_id):
    data = request.get_json()
    if not data:
        return jsonify({
            'code': 400,
            'message': '请求参数不能为空',
            'data': None
        }), 400

    result = PropertyBillService.update_bill(bill_id, **data)
    if result['success']:
        return jsonify({
            'code': 200,
            'message': result['message'],
            'data': result['data']
        }), 200
    else:
        return jsonify({
            'code': 404,
            'message': result['message'],
            'data': None
        }), 404


@property_bill_bp.route('/<int:bill_id>/pay', methods=['POST'])
def pay_bill(bill_id):
    data = request.get_json()
    if not data:
        return jsonify({
            'code': 400,
            'message': '请求参数不能为空',
            'data': None
        }), 400

    amount = data.get('amount')
    if amount is None:
        return jsonify({
            'code': 400,
            'message': '缺少 amount 参数',
            'data': None
        }), 400

    result = PropertyBillService.pay_bill(bill_id, float(amount))
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


@property_bill_bp.route('/summary', methods=['GET'])
def get_summary():
    plate_number = request.args.get('plate_number')
    if not plate_number:
        return jsonify({
            'code': 400,
            'message': '缺少 plate_number 参数',
            'data': None
        }), 400

    result = PropertyBillService.get_outstanding_summary(plate_number)
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': result['data']
    }), 200
