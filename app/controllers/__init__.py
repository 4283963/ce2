from .gate_controller import gate_bp
from .billing_controller import billing_bp
from .payment_controller import payment_bp
from .vehicle_controller import vehicle_bp
from .blacklist_controller import blacklist_bp
from .property_bill_controller import property_bill_bp

__all__ = [
    'gate_bp',
    'billing_bp',
    'payment_bp',
    'vehicle_bp',
    'blacklist_bp',
    'property_bill_bp'
]
