from datetime import datetime
from app.dao import GateDeviceDAO, VehicleDAO, VehicleRecordDAO, ParkingOrderDAO
from app.utils.common import generate_order_no


class GateService:

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

        vehicle = VehicleDAO.get_by_plate(plate_number)
        if not vehicle:
            vehicle = VehicleDAO.create(
                plate_number=plate_number,
                vehicle_type='visitor'
            )

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

        if direction == 'in':
            pending_order = ParkingOrderDAO.get_pending_by_plate(plate_number)
            if not pending_order:
                order_no = generate_order_no()
                order = ParkingOrderDAO.create(
                    order_no=order_no,
                    plate_number=plate_number,
                    entry_time=record_time,
                    status='pending'
                )
                result_data['order_no'] = order_no
                result_data['entry_time'] = record_time.strftime('%Y-%m-%d %H:%M:%S')
            else:
                result_data['order_no'] = pending_order.order_no
                result_data['entry_time'] = pending_order.entry_time.strftime('%Y-%m-%d %H:%M:%S')

        return {
            'success': True,
            'message': '数据接收成功',
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
