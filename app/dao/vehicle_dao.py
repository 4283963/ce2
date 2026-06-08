from sqlalchemy.exc import SQLAlchemyError
from app.models import Vehicle, db
from app.utils.db_utils import with_db_retry, db_commit


class VehicleDAO:

    @staticmethod
    @with_db_retry(max_retries=3)
    def get_by_plate(plate_number):
        return Vehicle.query.filter_by(plate_number=plate_number).first()

    @staticmethod
    @with_db_retry(max_retries=3)
    def get_by_id(vehicle_id):
        return Vehicle.query.get(vehicle_id)

    @staticmethod
    @with_db_retry(max_retries=3)
    def list_all(vehicle_type=None, page=1, page_size=20):
        query = Vehicle.query
        if vehicle_type:
            query = query.filter_by(vehicle_type=vehicle_type)
        return query.order_by(Vehicle.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    @staticmethod
    def create(plate_number, vehicle_type='visitor', owner_name=None, owner_phone=None):
        try:
            vehicle = Vehicle(
                plate_number=plate_number,
                vehicle_type=vehicle_type,
                owner_name=owner_name,
                owner_phone=owner_phone
            )
            db.session.add(vehicle)
            db_commit()
            return vehicle
        except SQLAlchemyError:
            db.session.rollback()
            raise

    @staticmethod
    def update(vehicle_id, **kwargs):
        try:
            vehicle = Vehicle.query.get(vehicle_id)
            if not vehicle:
                return None
            for key, value in kwargs.items():
                if hasattr(vehicle, key):
                    setattr(vehicle, key, value)
            db_commit()
            return vehicle
        except SQLAlchemyError:
            db.session.rollback()
            raise

    @staticmethod
    def delete(vehicle_id):
        try:
            vehicle = Vehicle.query.get(vehicle_id)
            if vehicle:
                db.session.delete(vehicle)
                db_commit()
                return True
            return False
        except SQLAlchemyError:
            db.session.rollback()
            raise

    @staticmethod
    @with_db_retry(max_retries=3)
    def is_resident(plate_number):
        vehicle = Vehicle.query.filter_by(plate_number=plate_number).first()
        if vehicle and vehicle.vehicle_type == 'resident':
            return True
        return False
