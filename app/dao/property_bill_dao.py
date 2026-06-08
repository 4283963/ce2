from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, and_
from app.models import PropertyBill, db
from app.utils.db_utils import with_db_retry, db_commit


class PropertyBillDAO:

    @staticmethod
    @with_db_retry(max_retries=3)
    def get_by_id(bill_id):
        return PropertyBill.query.get(bill_id)

    @staticmethod
    @with_db_retry(max_retries=3)
    def get_by_bill_no(bill_no):
        return PropertyBill.query.filter_by(bill_no=bill_no).first()

    @staticmethod
    @with_db_retry(max_retries=3)
    def list_by_plate(plate_number, status=None, page=1, page_size=20):
        query = PropertyBill.query.filter_by(plate_number=plate_number)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(PropertyBill.bill_month.desc())\
            .offset((page - 1) * page_size)\
            .limit(page_size).all()

    @staticmethod
    @with_db_retry(max_retries=3)
    def count_unpaid_overdue(plate_number, months=3):
        today = datetime.now().date()
        return PropertyBill.query.filter(
            and_(
                PropertyBill.plate_number == plate_number,
                PropertyBill.status == 'unpaid',
                PropertyBill.due_date.isnot(None),
                PropertyBill.due_date <= today,
                func.julianday(today) - func.julianday(PropertyBill.due_date) >= (months * 30)
            )
        ).count()

    @staticmethod
    @with_db_retry(max_retries=3)
    def get_unpaid_overdue_bills(plate_number, months=3):
        today = datetime.now().date()
        return PropertyBill.query.filter(
            and_(
                PropertyBill.plate_number == plate_number,
                PropertyBill.status == 'unpaid',
                PropertyBill.due_date.isnot(None),
                PropertyBill.due_date <= today,
                func.julianday(today) - func.julianday(PropertyBill.due_date) >= (months * 30)
            )
        ).order_by(PropertyBill.bill_month.asc()).all()

    @staticmethod
    @with_db_retry(max_retries=3)
    def get_total_outstanding(plate_number):
        result = db.session.query(
            func.sum(PropertyBill.total_amount - PropertyBill.paid_amount)
        ).filter(
            PropertyBill.plate_number == plate_number,
            PropertyBill.status == 'unpaid'
        ).scalar()
        return float(result) if result else 0.0

    @staticmethod
    def create(bill_no, plate_number, bill_month, total_amount,
               paid_amount=0.0, status='unpaid', owner_name=None, due_date=None):
        try:
            bill = PropertyBill(
                bill_no=bill_no,
                plate_number=plate_number,
                owner_name=owner_name,
                bill_month=bill_month,
                total_amount=total_amount,
                paid_amount=paid_amount,
                status=status,
                due_date=due_date
            )
            db.session.add(bill)
            db_commit()
            return bill
        except SQLAlchemyError:
            db.session.rollback()
            raise

    @staticmethod
    def update(bill_id, **kwargs):
        try:
            bill = PropertyBill.query.get(bill_id)
            if not bill:
                return None
            for key, value in kwargs.items():
                if hasattr(bill, key):
                    setattr(bill, key, value)
            db_commit()
            return bill
        except SQLAlchemyError:
            db.session.rollback()
            raise

    @staticmethod
    def pay_bill(bill_id, amount):
        try:
            bill = PropertyBill.query.get(bill_id)
            if not bill:
                return None
            new_paid = float(bill.paid_amount) + float(amount)
            bill.paid_amount = new_paid
            if new_paid >= float(bill.total_amount):
                bill.status = 'paid'
            else:
                bill.status = 'partial'
            db_commit()
            return bill
        except SQLAlchemyError:
            db.session.rollback()
            raise
