from sqlalchemy.exc import SQLAlchemyError
from app.models import GateDevice, db
from app.utils.db_utils import with_db_retry, db_commit


class GateDeviceDAO:

    @staticmethod
    @with_db_retry(max_retries=3)
    def get_by_device_code(device_code):
        return GateDevice.query.filter_by(device_code=device_code).first()

    @staticmethod
    @with_db_retry(max_retries=3)
    def get_by_id(gate_id):
        return GateDevice.query.get(gate_id)

    @staticmethod
    @with_db_retry(max_retries=3)
    def list_all():
        return GateDevice.query.all()

    @staticmethod
    def create(device_code, device_name, location=None, status=1):
        try:
            device = GateDevice(
                device_code=device_code,
                device_name=device_name,
                location=location,
                status=status
            )
            db.session.add(device)
            db_commit()
            return device
        except SQLAlchemyError:
            db.session.rollback()
            raise

    @staticmethod
    def update(gate_id, **kwargs):
        try:
            device = GateDevice.query.get(gate_id)
            if not device:
                return None
            for key, value in kwargs.items():
                if hasattr(device, key):
                    setattr(device, key, value)
            db_commit()
            return device
        except SQLAlchemyError:
            db.session.rollback()
            raise
