from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from app.models import PaymentTransaction, db
from app.utils.db_utils import with_db_retry, db_commit


class PaymentTransactionDAO:

    @staticmethod
    @with_db_retry(max_retries=3)
    def get_by_id(transaction_id):
        return PaymentTransaction.query.get(transaction_id)

    @staticmethod
    @with_db_retry(max_retries=3)
    def get_by_transaction_no(transaction_no):
        return PaymentTransaction.query.filter_by(transaction_no=transaction_no).first()

    @staticmethod
    @with_db_retry(max_retries=3)
    def get_by_order_id(order_id):
        return PaymentTransaction.query.filter_by(order_id=order_id).first()

    @staticmethod
    def create(transaction_no, order_id, amount, pay_method, pay_status='pending'):
        try:
            transaction = PaymentTransaction(
                transaction_no=transaction_no,
                order_id=order_id,
                amount=amount,
                pay_method=pay_method,
                pay_status=pay_status
            )
            db.session.add(transaction)
            db_commit()
            return transaction
        except SQLAlchemyError:
            db.session.rollback()
            raise

    @staticmethod
    def update(transaction_id, **kwargs):
        try:
            transaction = PaymentTransaction.query.get(transaction_id)
            if not transaction:
                return None
            for key, value in kwargs.items():
                if hasattr(transaction, key):
                    setattr(transaction, key, value)
            db_commit()
            return transaction
        except SQLAlchemyError:
            db.session.rollback()
            raise

    @staticmethod
    def mark_paid(transaction_id, third_party_trade_no=None):
        try:
            transaction = PaymentTransaction.query.get(transaction_id)
            if not transaction:
                return None
            transaction.pay_status = 'success'
            transaction.pay_time = datetime.now()
            transaction.third_party_trade_no = third_party_trade_no
            db_commit()
            return transaction
        except SQLAlchemyError:
            db.session.rollback()
            raise

    @staticmethod
    @with_db_retry(max_retries=3)
    def list_by_order_id(order_id):
        return PaymentTransaction.query.filter_by(order_id=order_id)\
            .order_by(PaymentTransaction.created_at.desc()).all()
