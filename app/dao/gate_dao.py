from app.models import GateDevice, db


class GateDeviceDAO:

    @staticmethod
    def get_by_device_code(device_code):
        return GateDevice.query.filter_by(device_code=device_code).first()

    @staticmethod
    def get_by_id(gate_id):
        return GateDevice.query.get(gate_id)

    @staticmethod
    def list_all():
        return GateDevice.query.all()

    @staticmethod
    def create(device_code, device_name, location=None, status=1):
        device = GateDevice(
            device_code=device_code,
            device_name=device_name,
            location=location,
            status=status
        )
        db.session.add(device)
        db.session.commit()
        return device

    @staticmethod
    def update(gate_id, **kwargs):
        device = GateDevice.query.get(gate_id)
        if not device:
            return None
        for key, value in kwargs.items():
            if hasattr(device, key):
                setattr(device, key, value)
        db.session.commit()
        return device
