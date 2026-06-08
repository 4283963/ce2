from app.models import Vehicle, db


class VehicleDAO:

    @staticmethod
    def get_by_plate(plate_number):
        return Vehicle.query.filter_by(plate_number=plate_number).first()

    @staticmethod
    def get_by_id(vehicle_id):
        return Vehicle.query.get(vehicle_id)

    @staticmethod
    def list_all(vehicle_type=None, page=1, page_size=20):
        query = Vehicle.query
        if vehicle_type:
            query = query.filter_by(vehicle_type=vehicle_type)
        return query.order_by(Vehicle.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    @staticmethod
    def create(plate_number, vehicle_type='visitor', owner_name=None, owner_phone=None):
        vehicle = Vehicle(
            plate_number=plate_number,
            vehicle_type=vehicle_type,
            owner_name=owner_name,
            owner_phone=owner_phone
        )
        db.session.add(vehicle)
        db.session.commit()
        return vehicle

    @staticmethod
    def update(vehicle_id, **kwargs):
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return None
        for key, value in kwargs.items():
            if hasattr(vehicle, key):
                setattr(vehicle, key, value)
        db.session.commit()
        return vehicle

    @staticmethod
    def delete(vehicle_id):
        vehicle = Vehicle.query.get(vehicle_id)
        if vehicle:
            db.session.delete(vehicle)
            db.session.commit()
            return True
        return False

    @staticmethod
    def is_resident(plate_number):
        vehicle = Vehicle.query.filter_by(plate_number=plate_number).first()
        if vehicle and vehicle.vehicle_type == 'resident':
            return True
        return False
