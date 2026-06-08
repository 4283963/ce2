from flask import Blueprint, request, jsonify
from app.services import GateService

gate_bp = Blueprint('gate', __name__, url_prefix='/api/gate')


@gate_bp.route('/upload', methods=['POST'])
def upload_gate_data():
    data = request.get_json()
    if not data:
        return jsonify({
            'code': 400,
            'message': '请求参数不能为空',
            'data': None
        }), 400

    plate_number = data.get('plate_number')
    gate_code = data.get('gate_code')
    direction = data.get('direction')
    record_time = data.get('record_time')

    result = GateService.receive_gate_data(
        plate_number=plate_number,
        gate_code=gate_code,
        direction=direction,
        record_time=record_time
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


@gate_bp.route('/devices', methods=['GET'])
def list_devices():
    result = GateService.list_gate_devices()
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': result['data']
    }), 200


@gate_bp.route('/records', methods=['GET'])
def get_records():
    plate_number = request.args.get('plate_number')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))

    if not plate_number:
        return jsonify({
            'code': 400,
            'message': '缺少 plate_number 参数',
            'data': None
        }), 400

    result = GateService.get_vehicle_records(plate_number, page, page_size)
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': result['data'],
        'total': result['total']
    }), 200
