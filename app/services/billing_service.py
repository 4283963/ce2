import math
from datetime import datetime
from app.dao import RateConfigDAO, ParkingOrderDAO, VehicleDAO


class BillingService:

    @staticmethod
    def calculate_parking_fee(plate_number, exit_time=None):
        if not exit_time:
            exit_time = datetime.now()
        elif isinstance(exit_time, str):
            try:
                exit_time = datetime.strptime(exit_time, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return {
                    'success': False,
                    'message': 'exit_time 格式错误，应为 YYYY-MM-DD HH:MM:SS'
                }

        is_resident = VehicleDAO.is_resident(plate_number)
        if is_resident:
            return {
                'success': True,
                'data': {
                    'plate_number': plate_number,
                    'vehicle_type': 'resident',
                    'amount': 0.00,
                    'duration_minutes': 0,
                    'message': '业主车辆免费停车'
                }
            }

        order = ParkingOrderDAO.get_pending_by_plate(plate_number)
        if not order:
            return {
                'success': False,
                'message': '未找到进行中的停车订单，请确认车辆是否入场'
            }

        entry_time = order.entry_time
        duration_seconds = (exit_time - entry_time).total_seconds()
        duration_minutes = int(math.ceil(duration_seconds / 60))

        if duration_minutes <= 0:
            duration_minutes = 0

        rate_config = RateConfigDAO.get_by_type('visitor')
        if not rate_config:
            free_minutes = 30
            first_hour_price = 5.0
            per_hour_price = 3.0
            max_daily_price = 50.0
        else:
            free_minutes = rate_config.free_minutes
            first_hour_price = float(rate_config.first_hour_price)
            per_hour_price = float(rate_config.per_hour_price)
            max_daily_price = float(rate_config.max_daily_price)

        if duration_minutes <= free_minutes:
            amount = 0.00
        else:
            billable_minutes = duration_minutes - free_minutes
            billable_hours = math.ceil(billable_minutes / 60)

            if billable_hours <= 1:
                amount = first_hour_price
            else:
                amount = first_hour_price + (billable_hours - 1) * per_hour_price

            if amount > max_daily_price:
                amount = max_daily_price

        amount = round(amount, 2)

        return {
            'success': True,
            'data': {
                'order_no': order.order_no,
                'plate_number': plate_number,
                'vehicle_type': 'visitor',
                'entry_time': entry_time.strftime('%Y-%m-%d %H:%M:%S'),
                'exit_time': exit_time.strftime('%Y-%m-%d %H:%M:%S'),
                'duration_minutes': duration_minutes,
                'free_minutes': free_minutes,
                'amount': amount,
                'rate_detail': {
                    'first_hour_price': first_hour_price,
                    'per_hour_price': per_hour_price,
                    'max_daily_price': max_daily_price
                }
            }
        }

    @staticmethod
    def confirm_exit(plate_number, exit_time=None):
        if not exit_time:
            exit_time = datetime.now()
        elif isinstance(exit_time, str):
            try:
                exit_time = datetime.strptime(exit_time, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return {
                    'success': False,
                    'message': 'exit_time 格式错误，应为 YYYY-MM-DD HH:MM:SS'
                }

        order = ParkingOrderDAO.get_pending_by_plate(plate_number)
        if not order:
            return {
                'success': False,
                'message': '未找到进行中的停车订单'
            }

        fee_result = BillingService.calculate_parking_fee(plate_number, exit_time)
        if not fee_result['success']:
            return fee_result

        fee_data = fee_result['data']

        updated_order = ParkingOrderDAO.update(
            order.id,
            exit_time=exit_time,
            duration_minutes=fee_data['duration_minutes'],
            amount=fee_data['amount']
        )

        return {
            'success': True,
            'message': '出场确认成功',
            'data': updated_order.to_dict()
        }

    @staticmethod
    def get_order_detail(order_no):
        order = ParkingOrderDAO.get_by_order_no(order_no)
        if not order:
            return {
                'success': False,
                'message': '订单不存在'
            }
        return {
            'success': True,
            'data': order.to_dict()
        }

    @staticmethod
    def list_orders(plate_number=None, status=None, page=1, page_size=20):
        if plate_number:
            orders = ParkingOrderDAO.list_by_plate(plate_number, page, page_size)
        elif status:
            orders = ParkingOrderDAO.list_by_status(status, page, page_size)
        else:
            from app.models import ParkingOrder
            orders = ParkingOrder.query.order_by(ParkingOrder.created_at.desc())\
                .offset((page - 1) * page_size).limit(page_size).all()

        return {
            'success': True,
            'data': [o.to_dict() for o in orders],
            'page': page,
            'page_size': page_size
        }
