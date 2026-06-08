from datetime import datetime
from sqlalchemy.exc import IntegrityError
from app.dao import GateDeviceDAO, VehicleDAO, VehicleRecordDAO, ParkingOrderDAO
from app.utils.common import generate_order_no
from app.models import db


class GateService:

    @staticmethod
    def _get_or_create_vehicle(plate_number):
        vehicle = VehicleDAO.get_by_plate(plate_number)
        if vehicle:
            return vehicle

        try:
            vehicle = VehicleDAO.create(
                plate_number=plate_number,
                vehicle_type='visitor'
            )
            return vehicle
        except IntegrityError:
            db.session.rollback()
            vehicle = VehicleDAO.get_by_plate(plate_number)
            if vehicle:
                return vehicle
            raise

    @staticmethod
    def _check_blacklist_and_intercept(plate_number, gate_code, direction, order_id=None):
        from app.services.blacklist_service import BlacklistService
        blacklist_info = BlacklistService.check_blacklist(plate_number)
        intercept_flag = blacklist_info.get('is_blacklisted', False)

        if intercept_flag and direction == 'out':
            BlacklistService.create_intercept_record(
                plate_number=plate_number,
                intercept_reason=blacklist_info.get('intercept_reason', ''),
                order_id=order_id,
                gate_code=gate_code,
                direction=direction
            )

        return {
            'intercept_flag': intercept_flag,
            'intercept_reason': blacklist_info.get('intercept_reason'),
            'overdue_bill_count': blacklist_info.get('overdue_bill_count', 0),
            'total_outstanding': blacklist_info.get('total_outstanding', 0),
            'overdue_bills': blacklist_info.get('overdue_bills', [])
        }

    @staticmethod
    def receive_gate_data(plate_number, gate_code, direction, record_time=None):
        if not plate_number or not gate_code or not direction:
            return {
                'success': False,
                'message': '参数不完整'
            }

        if direction not in ('in', 'out'):
            return {
                'success': False,
                'message': 'direction 参数只能是 in 或 out'
            }

        gate_device = GateDeviceDAO.get_by_device_code(gate_code)
        if not gate_device:
            return {
                'success': False,
                'message': f'车闸设备 {gate_code} 不存在'
            }

        if gate_device.status != 1:
            return {
                'success': False,
                'message': '车闸设备未启用'
            }

        if record_time:
            if isinstance(record_time, str):
                try:
                    record_time = datetime.strptime(record_time, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    return {
                        'success': False,
                        'message': 'record_time 格式错误，应为 YYYY-MM-DD HH:MM:SS'
                    }
        else:
            record_time = datetime.now()

        vehicle = GateService._get_or_create_vehicle(plate_number)

        record = VehicleRecordDAO.create(
            plate_number=plate_number,
            gate_id=gate_device.id,
            direction=direction,
            record_time=record_time
        )

        result_data = {
            'record_id': record.id,
            'plate_number': plate_number,
            'gate_code': gate_code,
            'direction': direction,
            'record_time': record_time.strftime('%Y-%m-%d %H:%M:%S'),
            'vehicle_type': vehicle.vehicle_type
        }

        pending_order = None
        if direction == 'in':
            pending_order = ParkingOrderDAO.get_pending_by_plate(plate_number)
            if not pending_order:
                try:
                    order_no = generate_order_no()
                    order = ParkingOrderDAO.create(
                        order_no=order_no,
                        plate_number=plate_number,
                        entry_time=record_time,
                        status='pending'
                    )
                    result_data['order_no'] = order_no
                    result_data['entry_time'] = record_time.strftime('%Y-%m-%d %H:%M:%S')
                except IntegrityError:
                    db.session.rollback()
                    pending_order = ParkingOrderDAO.get_pending_by_plate(plate_number)
                    if pending_order:
                        result_data['order_no'] = pending_order.order_no
                        result_data['entry_time'] = pending_order.entry_time.strftime('%Y-%m-%d %H:%M:%S')
            else:
                result_data['order_no'] = pending_order.order_no
                result_data['entry_time'] = pending_order.entry_time.strftime('%Y-%m-%d %H:%M:%S')

        order_id = None
        if direction == 'out':
            pending_order = ParkingOrderDAO.get_pending_by_plate(plate_number)
            if pending_order:
                order_id = pending_order.id
                result_data['order_no'] = pending_order.order_no

        blacklist_data = GateService._check_blacklist_and_intercept(
            plate_number=plate_number,
            gate_code=gate_code,
            direction=direction,
            order_id=order_id
        )
        result_data.update(blacklist_data)

        if blacklist_data.get('intercept_flag'):
            message = '黑名单车辆，禁止通行，请先缴纳物业费'
        else:
            message = '数据接收成功'

        return {
            'success': True,
            'message': message,
            'data': result_data
        }

    @staticmethod
    def list_gate_devices():
        devices = GateDeviceDAO.list_all()
        return {
            'success': True,
            'data': [d.to_dict() for d in devices]
        }

    @staticmethod
    def get_vehicle_records(plate_number, page=1, page_size=20):
        records = VehicleRecordDAO.list_by_plate(plate_number, page, page_size)
        return {
            'success': True,
            'data': [r.to_dict() for r in records],
            'total': len(records)
        }
