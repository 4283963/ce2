from flask import Blueprint, request, jsonify
from app.dao import VehicleDAO

vehicle_bp = Blueprint('vehicle', __name__, url_prefix='/api/vehicle')


@vehicle_bp.route('/list', methods=['GET'])
def list_vehicles():
    vehicle_type = request.args.get('vehicle_type')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))

    vehicles = VehicleDAO.list_all(
        vehicle_type=vehicle_type,
        page=page,
        page_size=page_size
    )

    return jsonify({
        'code': 200,
        'message': 'success',
        'data': [v.to_dict() for v in vehicles],
        'page': page,
        'page_size': page_size
    }), 200


@vehicle_bp.route('/<plate_number>', methods=['GET'])
def get_vehicle(plate_number):
    vehicle = VehicleDAO.get_by_plate(plate_number)
    if not vehicle:
        return jsonify({
            'code': 404,
            'message': '车辆不存在',
            'data': None
        }), 404

    return jsonify({
        'code': 200,
        'message': 'success',
        'data': vehicle.to_dict()
    }), 200


@vehicle_bp.route('', methods=['POST'])
def create_vehicle():
    data = request.get_json()
    if not data:
        return jsonify({
            'code': 400,
            'message': '请求参数不能为空',
            'data': None
        }), 400

    plate_number = data.get('plate_number')
    vehicle_type = data.get('vehicle_type', 'visitor')
    owner_name = data.get('owner_name')
    owner_phone = data.get('owner_phone')

    if not plate_number:
        return jsonify({
            'code': 400,
            'message': '缺少 plate_number 参数',
            'data': None
        }), 400

    existing = VehicleDAO.get_by_plate(plate_number)
    if existing:
        return jsonify({
            'code': 400,
            'message': '车牌号已存在',
            'data': None
        }), 400

    vehicle = VehicleDAO.create(
        plate_number=plate_number,
        vehicle_type=vehicle_type,
        owner_name=owner_name,
        owner_phone=owner_phone
    )

    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': vehicle.to_dict()
    }), 200


@vehicle_bp.route('/<int:vehicle_id>', methods=['PUT'])
def update_vehicle(vehicle_id):
    data = request.get_json()
    if not data:
        return jsonify({
            'code': 400,
            'message': '请求参数不能为空',
            'data': None
        }), 400

    vehicle = VehicleDAO.update(vehicle_id, **data)
    if not vehicle:
        return jsonify({
            'code': 404,
            'message': '车辆不存在',
            'data': None
        }), 404

    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': vehicle.to_dict()
    }), 200


@vehicle_bp.route('/<int:vehicle_id>', methods=['DELETE'])
def delete_vehicle(vehicle_id):
    result = VehicleDAO.delete(vehicle_id)
    if not result:
        return jsonify({
            'code': 404,
            'message': '车辆不存在',
            'data': None
        }), 404

    return jsonify({
        'code': 200,
        'message': '删除成功',
        'data': None
    }), 200
