from app.dao import PropertyBillDAO
from app.utils.common import generate_transaction_no


class PropertyBillService:

    @staticmethod
    def get_bill_detail(bill_id):
        bill = PropertyBillDAO.get_by_id(bill_id)
        if not bill:
            return {
                'success': False,
                'message': '账单不存在'
            }
        return {
            'success': True,
            'data': bill.to_dict()
        }

    @staticmethod
    def get_bill_by_no(bill_no):
        bill = PropertyBillDAO.get_by_bill_no(bill_no)
        if not bill:
            return {
                'success': False,
                'message': '账单不存在'
            }
        return {
            'success': True,
            'data': bill.to_dict()
        }

    @staticmethod
    def list_bills(plate_number=None, status=None, page=1, page_size=20):
        if plate_number:
            bills = PropertyBillDAO.list_by_plate(plate_number, status, page, page_size)
        else:
            from app.models import PropertyBill
            query = PropertyBill.query
            if status:
                query = query.filter_by(status=status)
            bills = query.order_by(PropertyBill.bill_month.desc())\
                .offset((page - 1) * page_size)\
                .limit(page_size).all()

        return {
            'success': True,
            'data': [b.to_dict() for b in bills],
            'page': page,
            'page_size': page_size
        }

    @staticmethod
    def create_bill(plate_number, bill_month, total_amount,
                    owner_name=None, due_date=None, status='unpaid'):
        bill_no = 'WY' + bill_month.replace('-', '') + generate_transaction_no()[-6:]

        bill = PropertyBillDAO.create(
            bill_no=bill_no,
            plate_number=plate_number,
            bill_month=bill_month,
            total_amount=total_amount,
            paid_amount=0.0,
            status=status,
            owner_name=owner_name,
            due_date=due_date
        )

        return {
            'success': True,
            'message': '账单创建成功',
            'data': bill.to_dict()
        }

    @staticmethod
    def update_bill(bill_id, **kwargs):
        bill = PropertyBillDAO.update(bill_id, **kwargs)
        if not bill:
            return {
                'success': False,
                'message': '账单不存在'
            }
        return {
            'success': True,
            'message': '更新成功',
            'data': bill.to_dict()
        }

    @staticmethod
    def pay_bill(bill_id, amount):
        if amount <= 0:
            return {
                'success': False,
                'message': '缴费金额必须大于0'
            }

        bill = PropertyBillDAO.pay_bill(bill_id, amount)
        if not bill:
            return {
                'success': False,
                'message': '账单不存在'
            }

        return {
            'success': True,
            'message': '缴费成功',
            'data': bill.to_dict()
        }

    @staticmethod
    def get_outstanding_summary(plate_number):
        from app.models import PropertyBill
        bills = PropertyBillDAO.list_by_plate(plate_number, status='unpaid')
        total_outstanding = PropertyBillDAO.get_total_outstanding(plate_number)
        overdue_count = PropertyBillDAO.count_unpaid_overdue(plate_number, months=3)

        return {
            'success': True,
            'data': {
                'plate_number': plate_number,
                'total_outstanding': round(total_outstanding, 2),
                'unpaid_bill_count': len(bills),
                'overdue_bill_count': overdue_count,
                'is_blacklisted': overdue_count >= 3
            }
        }
