from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class GateDevice(db.Model):
    __tablename__ = 'gate_devices'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    device_code = db.Column(db.String(50), nullable=False, unique=True)
    device_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200))
    status = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'device_code': self.device_code,
            'device_name': self.device_name,
            'location': self.location,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class Vehicle(db.Model):
    __tablename__ = 'vehicles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    plate_number = db.Column(db.String(20), nullable=False, unique=True)
    vehicle_type = db.Column(db.String(20), nullable=False, default='visitor')
    owner_name = db.Column(db.String(50))
    owner_phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'plate_number': self.plate_number,
            'vehicle_type': self.vehicle_type,
            'owner_name': self.owner_name,
            'owner_phone': self.owner_phone,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class VehicleRecord(db.Model):
    __tablename__ = 'vehicle_records'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    plate_number = db.Column(db.String(20), nullable=False, index=True)
    gate_id = db.Column(db.Integer)
    direction = db.Column(db.String(10), nullable=False)
    record_time = db.Column(db.DateTime, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'plate_number': self.plate_number,
            'gate_id': self.gate_id,
            'direction': self.direction,
            'record_time': self.record_time.strftime('%Y-%m-%d %H:%M:%S') if self.record_time else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class ParkingOrder(db.Model):
    __tablename__ = 'parking_orders'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_no = db.Column(db.String(32), nullable=False, unique=True)
    plate_number = db.Column(db.String(20), nullable=False, index=True)
    entry_time = db.Column(db.DateTime, nullable=False)
    exit_time = db.Column(db.DateTime)
    duration_minutes = db.Column(db.Integer, default=0)
    amount = db.Column(db.Numeric(10, 2), default=0.00)
    status = db.Column(db.String(20), nullable=False, default='pending', index=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'order_no': self.order_no,
            'plate_number': self.plate_number,
            'entry_time': self.entry_time.strftime('%Y-%m-%d %H:%M:%S') if self.entry_time else None,
            'exit_time': self.exit_time.strftime('%Y-%m-%d %H:%M:%S') if self.exit_time else None,
            'duration_minutes': self.duration_minutes,
            'amount': float(self.amount) if self.amount else 0.0,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class PaymentTransaction(db.Model):
    __tablename__ = 'payment_transactions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    transaction_no = db.Column(db.String(32), nullable=False, unique=True)
    order_id = db.Column(db.Integer, nullable=False, index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    pay_method = db.Column(db.String(20), nullable=False)
    pay_status = db.Column(db.String(20), nullable=False, default='pending', index=True)
    pay_time = db.Column(db.DateTime)
    third_party_trade_no = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'transaction_no': self.transaction_no,
            'order_id': self.order_id,
            'amount': float(self.amount) if self.amount else 0.0,
            'pay_method': self.pay_method,
            'pay_status': self.pay_status,
            'pay_time': self.pay_time.strftime('%Y-%m-%d %H:%M:%S') if self.pay_time else None,
            'third_party_trade_no': self.third_party_trade_no,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class RateConfig(db.Model):
    __tablename__ = 'rate_configs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rate_type = db.Column(db.String(20), nullable=False, default='visitor')
    free_minutes = db.Column(db.Integer, default=30)
    first_hour_price = db.Column(db.Numeric(10, 2), default=5.00)
    per_hour_price = db.Column(db.Numeric(10, 2), default=3.00)
    max_daily_price = db.Column(db.Numeric(10, 2), default=50.00)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'rate_type': self.rate_type,
            'free_minutes': self.free_minutes,
            'first_hour_price': float(self.first_hour_price) if self.first_hour_price else 0.0,
            'per_hour_price': float(self.per_hour_price) if self.per_hour_price else 0.0,
            'max_daily_price': float(self.max_daily_price) if self.max_daily_price else 0.0,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class PropertyBill(db.Model):
    __tablename__ = 'property_bills'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bill_no = db.Column(db.String(32), nullable=False, unique=True)
    plate_number = db.Column(db.String(20), nullable=False, index=True)
    owner_name = db.Column(db.String(50))
    bill_month = db.Column(db.String(7), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    paid_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    status = db.Column(db.String(20), nullable=False, default='unpaid', index=True)
    due_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'bill_no': self.bill_no,
            'plate_number': self.plate_number,
            'owner_name': self.owner_name,
            'bill_month': self.bill_month,
            'total_amount': float(self.total_amount) if self.total_amount else 0.0,
            'paid_amount': float(self.paid_amount) if self.paid_amount else 0.0,
            'outstanding_amount': float(self.total_amount - self.paid_amount) if self.total_amount and self.paid_amount else 0.0,
            'status': self.status,
            'due_date': self.due_date.strftime('%Y-%m-%d') if self.due_date else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class InterceptRecord(db.Model):
    __tablename__ = 'intercept_records'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    plate_number = db.Column(db.String(20), nullable=False, index=True)
    intercept_time = db.Column(db.DateTime, nullable=False, index=True)
    intercept_reason = db.Column(db.String(200), nullable=False)
    order_id = db.Column(db.Integer)
    gate_code = db.Column(db.String(50))
    direction = db.Column(db.String(10))
    status = db.Column(db.String(20), nullable=False, default='intercepted', index=True)
    handler = db.Column(db.String(50))
    handle_time = db.Column(db.DateTime)
    remark = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'plate_number': self.plate_number,
            'intercept_time': self.intercept_time.strftime('%Y-%m-%d %H:%M:%S') if self.intercept_time else None,
            'intercept_reason': self.intercept_reason,
            'order_id': self.order_id,
            'gate_code': self.gate_code,
            'direction': self.direction,
            'status': self.status,
            'handler': self.handler,
            'handle_time': self.handle_time.strftime('%Y-%m-%d %H:%M:%S') if self.handle_time else None,
            'remark': self.remark,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
