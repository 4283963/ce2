from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from app.models import VehicleRecord, db
from app.utils.db_utils import with_db_retry, db_commit


class VehicleRecordDAO:

    @staticmethod
    @with_db_retry(max_retries=3)
    def get_by_id(record_id):
        return VehicleRecord.query.get(record_id)

    @staticmethod
    def create(plate_number, gate_id, direction, record_time=None):
        try:
            record = VehicleRecord(
                plate_number=plate_number,
                gate_id=gate_id,
                direction=direction,
                record_time=record_time or datetime.now()
            )
            db.session.add(record)
            db_commit()
            return record
        except SQLAlchemyError:
            db.session.rollback()
            raise

    @staticmethod
    @with_db_retry(max_retries=3)
    def list_by_plate(plate_number, page=1, page_size=20):
        return VehicleRecord.query.filter_by(plate_number=plate_number)\
            .order_by(VehicleRecord.record_time.desc())\
            .offset((page - 1) * page_size)\
            .limit(page_size).all()

    @staticmethod
    @with_db_retry(max_retries=3)
    def get_latest_entry(plate_number):
        return VehicleRecord.query.filter_by(plate_number=plate_number, direction='in')\
            .order_by(VehicleRecord.record_time.desc())\
            .first()

    @staticmethod
    @with_db_retry(max_retries=3)
    def get_latest_record(plate_number):
        return VehicleRecord.query.filter_by(plate_number=plate_number)\
            .order_by(VehicleRecord.record_time.desc())\
            .first()
