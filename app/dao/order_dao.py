from app.models import ParkingOrder, db


class ParkingOrderDAO:

    @staticmethod
    def get_by_id(order_id):
        return ParkingOrder.query.get(order_id)

    @staticmethod
    def get_by_order_no(order_no):
        return ParkingOrder.query.filter_by(order_no=order_no).first()

    @staticmethod
    def get_pending_by_plate(plate_number):
        return ParkingOrder.query.filter_by(plate_number=plate_number, status='pending')\
            .order_by(ParkingOrder.created_at.desc())\
            .first()

    @staticmethod
    def create(order_no, plate_number, entry_time, status='pending'):
        order = ParkingOrder(
            order_no=order_no,
            plate_number=plate_number,
            entry_time=entry_time,
            status=status
        )
        db.session.add(order)
        db.session.commit()
        return order

    @staticmethod
    def update(order_id, **kwargs):
        order = ParkingOrder.query.get(order_id)
        if not order:
            return None
        for key, value in kwargs.items():
            if hasattr(order, key):
                setattr(order, key, value)
        db.session.commit()
        return order

    @staticmethod
    def list_by_plate(plate_number, page=1, page_size=20):
        return ParkingOrder.query.filter_by(plate_number=plate_number)\
            .order_by(ParkingOrder.created_at.desc())\
            .offset((page - 1) * page_size)\
            .limit(page_size).all()

    @staticmethod
    def list_by_status(status, page=1, page_size=20):
        return ParkingOrder.query.filter_by(status=status)\
            .order_by(ParkingOrder.created_at.desc())\
            .offset((page - 1) * page_size)\
            .limit(page_size).all()
