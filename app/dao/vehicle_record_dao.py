from datetime import datetime
from app.models import VehicleRecord, db


class VehicleRecordDAO:

    @staticmethod
    def get_by_id(record_id):
        return VehicleRecord.query.get(record_id)

    @staticmethod
    def create(plate_number, gate_id, direction, record_time=None):
        record = VehicleRecord(
            plate_number=plate_number,
            gate_id=gate_id,
            direction=direction,
            record_time=record_time or datetime.now()
        )
        db.session.add(record)
        db.session.commit()
        return record

    @staticmethod
    def list_by_plate(plate_number, page=1, page_size=20):
        return VehicleRecord.query.filter_by(plate_number=plate_number)\
            .order_by(VehicleRecord.record_time.desc())\
            .offset((page - 1) * page_size)\
            .limit(page_size).all()

    @staticmethod
    def get_latest_entry(plate_number):
        return VehicleRecord.query.filter_by(plate_number=plate_number, direction='in')\
            .order_by(VehicleRecord.record_time.desc())\
            .first()

    @staticmethod
    def get_latest_record(plate_number):
        return VehicleRecord.query.filter_by(plate_number=plate_number)\
            .order_by(VehicleRecord.record_time.desc())\
            .first()
