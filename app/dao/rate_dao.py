from app.models import RateConfig, db


class RateConfigDAO:

    @staticmethod
    def get_by_id(rate_id):
        return RateConfig.query.get(rate_id)

    @staticmethod
    def get_by_type(rate_type='visitor'):
        return RateConfig.query.filter_by(rate_type=rate_type).first()

    @staticmethod
    def list_all():
        return RateConfig.query.all()

    @staticmethod
    def create(rate_type='visitor', free_minutes=30, first_hour_price=5.0,
               per_hour_price=3.0, max_daily_price=50.0):
        config = RateConfig(
            rate_type=rate_type,
            free_minutes=free_minutes,
            first_hour_price=first_hour_price,
            per_hour_price=per_hour_price,
            max_daily_price=max_daily_price
        )
        db.session.add(config)
        db.session.commit()
        return config

    @staticmethod
    def update(rate_id, **kwargs):
        config = RateConfig.query.get(rate_id)
        if not config:
            return None
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        db.session.commit()
        return config
