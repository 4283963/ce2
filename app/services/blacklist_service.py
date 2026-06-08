from datetime import datetime
from app.dao import PropertyBillDAO, InterceptRecordDAO


class BlacklistService:

    OVERDUE_MONTHS_THRESHOLD = 3

    @staticmethod
    def check_blacklist(plate_number):
        overdue_count = PropertyBillDAO.count_unpaid_overdue(
            plate_number,
            months=BlacklistService.OVERDUE_MONTHS_THRESHOLD
        )

        is_blacklisted = overdue_count > 0

        result = {
            'plate_number': plate_number,
            'is_blacklisted': is_blacklisted,
            'overdue_bill_count': overdue_count
        }

        if is_blacklisted:
            overdue_bills = PropertyBillDAO.get_unpaid_overdue_bills(
                plate_number,
                months=BlacklistService.OVERDUE_MONTHS_THRESHOLD
            )
            total_outstanding = PropertyBillDAO.get_total_outstanding(plate_number)

            bill_details = []
            for bill in overdue_bills:
                bill_details.append({
                    'bill_no': bill.bill_no,
                    'bill_month': bill.bill_month,
                    'total_amount': float(bill.total_amount),
                    'paid_amount': float(bill.paid_amount),
                    'outstanding': float(bill.total_amount - bill.paid_amount),
                    'due_date': bill.due_date.strftime('%Y-%m-%d') if bill.due_date else None
                })

            result['intercept_flag'] = True
            result['intercept_reason'] = f'该车辆关联业主累计有 {overdue_count} 个月物业费逾期未缴（逾期超过 {BlacklistService.OVERDUE_MONTHS_THRESHOLD} 个月），已被列入黑名单，请先缴纳欠费后再出场'
            result['total_outstanding'] = round(total_outstanding, 2)
            result['overdue_bills'] = bill_details
        else:
            result['intercept_flag'] = False
            result['intercept_reason'] = None

        return result

    @staticmethod
    def create_intercept_record(plate_number, intercept_reason, order_id=None,
                                gate_code=None, direction=None, remark=None):
        record = InterceptRecordDAO.create(
            plate_number=plate_number,
            intercept_reason=intercept_reason,
            order_id=order_id,
            gate_code=gate_code,
            direction=direction,
            status='intercepted',
            remark=remark
        )
        return {
            'success': True,
            'data': record.to_dict()
        }

    @staticmethod
    def get_blacklist_info(plate_number):
        blacklist_info = BlacklistService.check_blacklist(plate_number)
        return {
            'success': True,
            'data': blacklist_info
        }

    @staticmethod
    def list_intercept_records(plate_number=None, status=None, page=1, page_size=20):
        if plate_number:
            records = InterceptRecordDAO.list_by_plate(plate_number, page, page_size)
        elif status:
            records = InterceptRecordDAO.list_by_status(status, page, page_size)
        else:
            records = InterceptRecordDAO.list_all(page, page_size)

        return {
            'success': True,
            'data': [r.to_dict() for r in records],
            'page': page,
            'page_size': page_size
        }

    @staticmethod
    def resolve_intercept(record_id, handler, remark=None):
        record = InterceptRecordDAO.resolve(record_id, handler, remark)
        if not record:
            return {
                'success': False,
                'message': '拦截记录不存在'
            }
        return {
            'success': True,
            'message': '已放行',
            'data': record.to_dict()
        }
