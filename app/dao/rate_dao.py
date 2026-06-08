from sqlalchemy.exc import SQLAlchemyError
from app.models import RateConfig, db
from app.utils.db_utils import with_db_retry, db_commit


class RateConfigDAO:

    @staticmethod
    @with_db_retry(max_retries=3)
    def get_by_id(rate_id):
        return RateConfig.query.get(rate_id)

    @staticmethod
    @with_db_retry(max_retries=3)
    def get_by_type(rate_type='visitor'):
        return RateConfig.query.filter_by(rate_type=rate_type).first()

    @staticmethod
    @with_db_retry(max_retries=3)
    def list_all():
        return RateConfig.query.all()

    @staticmethod
    def create(rate_type='visitor', free_minutes=30, first_hour_price=5.0,
               per_hour_price=3.0, max_daily_price=50.0):
        try:
            config = RateConfig(
                rate_type=rate_type,
                free_minutes=free_minutes,
                first_hour_price=first_hour_price,
                per_hour_price=per_hour_price,
                max_daily_price=max_daily_price
            )
            db.session.add(config)
            db_commit()
            return config
        except SQLAlchemyError:
            db.session.rollback()
            raise

    @staticmethod
    def update(rate_id, **kwargs):
        try:
            config = RateConfig.query.get(rate_id)
            if not config:
                return None
            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            db_commit()
            return config
        except SQLAlchemyError:
            db.session.rollback()
            raise
