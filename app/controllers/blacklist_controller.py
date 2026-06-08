from flask import Blueprint, request, jsonify
from app.services import BlacklistService

blacklist_bp = Blueprint('blacklist', __name__, url_prefix='/api/blacklist')


@blacklist_bp.route('/check', methods=['POST'])
def check_blacklist():
    data = request.get_json()
    if not data:
        return jsonify({
            'code': 400,
            'message': '请求参数不能为空',
            'data': None
        }), 400

    plate_number = data.get('plate_number')
    if not plate_number:
        return jsonify({
            'code': 400,
            'message': '缺少 plate_number 参数',
            'data': None
        }), 400

    result = BlacklistService.get_blacklist_info(plate_number)
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': result['data']
    }), 200


@blacklist_bp.route('/intercepts', methods=['GET'])
def list_intercepts():
    plate_number = request.args.get('plate_number')
    status = request.args.get('status')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))

    result = BlacklistService.list_intercept_records(
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


@blacklist_bp.route('/intercept/<int:record_id>/resolve', methods=['POST'])
def resolve_intercept(record_id):
    data = request.get_json() or {}
    handler = data.get('handler')
    remark = data.get('remark')

    if not handler:
        return jsonify({
            'code': 400,
            'message': '缺少 handler 参数',
            'data': None
        }), 400

    result = BlacklistService.resolve_intercept(record_id, handler, remark)
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
