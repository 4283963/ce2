import uuid
import random
import time
from datetime import datetime
from app.dao import PaymentTransactionDAO, ParkingOrderDAO
from app.utils.common import generate_transaction_no


class PaymentService:

    @staticmethod
    def create_payment(order_id, pay_method='wechat'):
        if pay_method not in ('wechat', 'alipay'):
            return {
                'success': False,
                'message': '支付方式只能是 wechat 或 alipay'
            }

        order = ParkingOrderDAO.get_by_id(order_id)
        if not order:
            return {
                'success': False,
                'message': '订单不存在'
            }

        if order.status == 'paid':
            return {
                'success': False,
                'message': '订单已支付，请勿重复支付'
            }

        if float(order.amount) <= 0:
            ParkingOrderDAO.update(order_id, status='paid')
            transaction_no = generate_transaction_no()
            transaction = PaymentTransactionDAO.create(
                transaction_no=transaction_no,
                order_id=order_id,
                amount=order.amount,
                pay_method=pay_method,
                pay_status='success'
            )
            PaymentTransactionDAO.mark_paid(transaction.id, 'FREE_PAYMENT')
            return {
                'success': True,
                'message': '无需支付，已标记为已支付',
                'data': {
                    'transaction_no': transaction_no,
                    'order_no': order.order_no,
                    'amount': 0.00,
                    'pay_method': pay_method,
                    'pay_status': 'success'
                }
            }

        transaction_no = generate_transaction_no()
        transaction = PaymentTransactionDAO.create(
            transaction_no=transaction_no,
            order_id=order_id,
            amount=order.amount,
            pay_method=pay_method,
            pay_status='pending'
        )

        pay_result = PaymentService._mock_third_party_pay(
            transaction_no=transaction_no,
            amount=float(order.amount),
            pay_method=pay_method
        )

        if pay_result['success']:
            PaymentTransactionDAO.mark_paid(
                transaction.id,
                third_party_trade_no=pay_result['third_party_trade_no']
            )
            ParkingOrderDAO.update(order_id, status='paid')
            return {
                'success': True,
                'message': '支付成功',
                'data': {
                    'transaction_no': transaction_no,
                    'order_no': order.order_no,
                    'amount': float(order.amount),
                    'pay_method': pay_method,
                    'pay_status': 'success',
                    'third_party_trade_no': pay_result['third_party_trade_no'],
                    'pay_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            }
        else:
            PaymentTransactionDAO.update(
                transaction.id,
                pay_status='failed'
            )
            return {
                'success': False,
                'message': pay_result.get('message', '支付失败'),
                'data': {
                    'transaction_no': transaction_no,
                    'order_no': order.order_no,
                    'amount': float(order.amount),
                    'pay_method': pay_method,
                    'pay_status': 'failed'
                }
            }

    @staticmethod
    def _mock_third_party_pay(transaction_no, amount, pay_method):
        time.sleep(0.1)

        success = random.random() > 0.05

        if success:
            third_party_trade_no = ''
            if pay_method == 'wechat':
                third_party_trade_no = 'WX' + uuid.uuid4().hex[:20].upper()
            else:
                third_party_trade_no = 'ALI' + uuid.uuid4().hex[:20].upper()

            return {
                'success': True,
                'third_party_trade_no': third_party_trade_no,
                'transaction_no': transaction_no,
                'amount': amount,
                'pay_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        else:
            return {
                'success': False,
                'message': '支付失败：余额不足或网络异常'
            }

    @staticmethod
    def get_transaction_detail(transaction_no):
        transaction = PaymentTransactionDAO.get_by_transaction_no(transaction_no)
        if not transaction:
            return {
                'success': False,
                'message': '交易流水不存在'
            }
        return {
            'success': True,
            'data': transaction.to_dict()
        }

    @staticmethod
    def list_transactions(order_id=None):
        if order_id:
            transactions = PaymentTransactionDAO.list_by_order_id(order_id)
        else:
            from app.models import PaymentTransaction
            transactions = PaymentTransaction.query.order_by(
                PaymentTransaction.created_at.desc()
            ).limit(50).all()

        return {
            'success': True,
            'data': [t.to_dict() for t in transactions]
        }
