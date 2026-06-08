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
            parking_amount = 0.00
            duration_minutes = 0
            vehicle_type = 'resident'
            order_no = None
            entry_time = None
            free_minutes = 0
            rate_detail = None
            message = '业主车辆免费停车'
        else:
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
                parking_amount = 0.00
            else:
                billable_minutes = duration_minutes - free_minutes
                billable_hours = math.ceil(billable_minutes / 60)

                if billable_hours <= 1:
                    parking_amount = first_hour_price
                else:
                    parking_amount = first_hour_price + (billable_hours - 1) * per_hour_price

                if parking_amount > max_daily_price:
                    parking_amount = max_daily_price

            parking_amount = round(parking_amount, 2)
            vehicle_type = 'visitor'
            order_no = order.order_no
            message = None
            rate_detail = {
                'first_hour_price': first_hour_price,
                'per_hour_price': per_hour_price,
                'max_daily_price': max_daily_price
            }

        from app.services.blacklist_service import BlacklistService
        blacklist_info = BlacklistService.check_blacklist(plate_number)
        intercept_flag = blacklist_info.get('is_blacklisted', False)
        intercept_reason = blacklist_info.get('intercept_reason')
        overdue_bill_count = blacklist_info.get('overdue_bill_count', 0)
        total_outstanding = blacklist_info.get('total_outstanding', 0)
        overdue_bills = blacklist_info.get('overdue_bills', [])

        result_data = {
            'order_no': order_no,
            'plate_number': plate_number,
            'vehicle_type': vehicle_type,
            'entry_time': entry_time.strftime('%Y-%m-%d %H:%M:%S') if entry_time else None,
            'exit_time': exit_time.strftime('%Y-%m-%d %H:%M:%S'),
            'duration_minutes': duration_minutes,
            'free_minutes': free_minutes,
            'parking_amount': parking_amount,
            'total_amount': parking_amount,
            'rate_detail': rate_detail,
            'intercept_flag': intercept_flag,
            'intercept_reason': intercept_reason,
            'overdue_bill_count': overdue_bill_count,
            'total_outstanding': total_outstanding,
            'overdue_bills': overdue_bills
        }

        if message:
            result_data['message'] = message

        return {
            'success': True,
            'data': result_data
        }

    @staticmethod
    def confirm_exit(plate_number, exit_time=None, gate_code=None):
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

        if not is_resident:
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

        updated_order = None
        if not is_resident:
            order = ParkingOrderDAO.get_pending_by_plate(plate_number)
            if order:
                updated_order = ParkingOrderDAO.update(
                    order.id,
                    exit_time=exit_time,
                    duration_minutes=fee_data['duration_minutes'],
                    amount=fee_data['parking_amount']
                )

        if fee_data.get('intercept_flag'):
            from app.services.blacklist_service import BlacklistService
            order_id = updated_order.id if updated_order else None
            BlacklistService.create_intercept_record(
                plate_number=plate_number,
                intercept_reason=fee_data.get('intercept_reason', ''),
                order_id=order_id,
                gate_code=gate_code,
                direction='out'
            )

        result_data = fee_data
        if updated_order:
            result_data['order'] = updated_order.to_dict()

        return {
            'success': True,
            'message': '出场确认成功',
            'data': result_data
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
