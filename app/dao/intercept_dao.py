from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from app.models import InterceptRecord, db
from app.utils.db_utils import with_db_retry, db_commit


class InterceptRecordDAO:

    @staticmethod
    @with_db_retry(max_retries=3)
    def get_by_id(record_id):
        return InterceptRecord.query.get(record_id)

    @staticmethod
    def create(plate_number, intercept_reason, order_id=None, gate_code=None,
               direction=None, status='intercepted', remark=None, intercept_time=None):
        try:
            record = InterceptRecord(
                plate_number=plate_number,
                intercept_time=intercept_time or datetime.now(),
                intercept_reason=intercept_reason,
                order_id=order_id,
                gate_code=gate_code,
                direction=direction,
                status=status,
                remark=remark
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
        return InterceptRecord.query.filter_by(plate_number=plate_number)\
            .order_by(InterceptRecord.intercept_time.desc())\
            .offset((page - 1) * page_size)\
            .limit(page_size).all()

    @staticmethod
    @with_db_retry(max_retries=3)
    def list_by_status(status, page=1, page_size=20):
        return InterceptRecord.query.filter_by(status=status)\
            .order_by(InterceptRecord.intercept_time.desc())\
            .offset((page - 1) * page_size)\
            .limit(page_size).all()

    @staticmethod
    @with_db_retry(max_retries=3)
    def list_all(page=1, page_size=20):
        return InterceptRecord.query.order_by(InterceptRecord.intercept_time.desc())\
            .offset((page - 1) * page_size)\
            .limit(page_size).all()

    @staticmethod
    def resolve(record_id, handler, remark=None):
        try:
            record = InterceptRecord.query.get(record_id)
            if not record:
                return None
            record.status = 'released'
            record.handler = handler
            record.handle_time = datetime.now()
            if remark:
                record.remark = remark
            db_commit()
            return record
        except SQLAlchemyError:
            db.session.rollback()
            raise
