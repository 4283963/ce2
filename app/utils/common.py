import uuid
import time


def generate_order_no():
    timestamp = time.strftime('%Y%m%d%H%M%S')
    uuid_str = uuid.uuid4().hex[:8].upper()
    return f'P{timestamp}{uuid_str}'


def generate_transaction_no():
    timestamp = time.strftime('%Y%m%d%H%M%S')
    uuid_str = uuid.uuid4().hex[:10].upper()
    return f'T{timestamp}{uuid_str}'
