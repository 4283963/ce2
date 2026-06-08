from datetime import datetime
from app.models import PaymentTransaction, db


class PaymentTransactionDAO:

    @staticmethod
    def get_by_id(transaction_id):
        return PaymentTransaction.query.get(transaction_id)

    @staticmethod
    def get_by_transaction_no(transaction_no):
        return PaymentTransaction.query.filter_by(transaction_no=transaction_no).first()

    @staticmethod
    def get_by_order_id(order_id):
        return PaymentTransaction.query.filter_by(order_id=order_id).first()

    @staticmethod
    def create(transaction_no, order_id, amount, pay_method, pay_status='pending'):
        transaction = PaymentTransaction(
            transaction_no=transaction_no,
            order_id=order_id,
            amount=amount,
            pay_method=pay_method,
            pay_status=pay_status
        )
        db.session.add(transaction)
        db.session.commit()
        return transaction

    @staticmethod
    def update(transaction_id, **kwargs):
        transaction = PaymentTransaction.query.get(transaction_id)
        if not transaction:
            return None
        for key, value in kwargs.items():
            if hasattr(transaction, key):
                setattr(transaction, key, value)
        db.session.commit()
        return transaction

    @staticmethod
    def mark_paid(transaction_id, third_party_trade_no=None):
        transaction = PaymentTransaction.query.get(transaction_id)
        if not transaction:
            return None
        transaction.pay_status = 'success'
        transaction.pay_time = datetime.now()
        transaction.third_party_trade_no = third_party_trade_no
        db.session.commit()
        return transaction

    @staticmethod
    def list_by_order_id(order_id):
        return PaymentTransaction.query.filter_by(order_id=order_id)\
            .order_by(PaymentTransaction.created_at.desc()).all()
