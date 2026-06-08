import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import date, datetime
from app import create_app
from app.models import db
from app.dao import RateConfigDAO, GateDeviceDAO, VehicleDAO, PropertyBillDAO


def _parse_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d').date()


def init_database():
    app = create_app()

    with app.app_context():
        db.create_all()
        print('数据库表创建成功')

        if not RateConfigDAO.get_by_type('visitor'):
            RateConfigDAO.create(
                rate_type='visitor',
                free_minutes=30,
                first_hour_price=5.0,
                per_hour_price=3.0,
                max_daily_price=50.0
            )
            print('费率配置初始化成功')

        if not GateDeviceDAO.get_by_device_code('GATE-001'):
            GateDeviceDAO.create('GATE-001', '东门入口', '小区东门', 1)
            GateDeviceDAO.create('GATE-002', '东门出口', '小区东门', 1)
            GateDeviceDAO.create('GATE-003', '西门入口', '小区西门', 1)
            GateDeviceDAO.create('GATE-004', '西门出口', '小区西门', 1)
            print('车闸设备初始化成功')

        if not VehicleDAO.get_by_plate('京A12345'):
            VehicleDAO.create('京A12345', 'resident', '张三', '13800138001')
            VehicleDAO.create('京B67890', 'resident', '李四', '13800138002')
            print('测试车辆数据初始化成功')

        if not PropertyBillDAO.get_by_bill_no('WY202509001'):
            PropertyBillDAO.create(
                'WY202509001', '京A12345', '2025-09', 350.00, 350.00,
                'paid', '张三', _parse_date('2025-10-01')
            )
            PropertyBillDAO.create(
                'WY202510001', '京A12345', '2025-10', 350.00, 350.00,
                'paid', '张三', _parse_date('2025-11-01')
            )
            PropertyBillDAO.create(
                'WY202511001', '京A12345', '2025-11', 350.00, 0.00,
                'unpaid', '张三', _parse_date('2025-12-01')
            )
            PropertyBillDAO.create(
                'WY202512001', '京A12345', '2025-12', 350.00, 0.00,
                'unpaid', '张三', _parse_date('2026-01-01')
            )
            PropertyBillDAO.create(
                'WY202601001', '京A12345', '2026-01', 350.00, 0.00,
                'unpaid', '张三', _parse_date('2026-02-01')
            )
            PropertyBillDAO.create(
                'WY202602001', '京A12345', '2026-02', 350.00, 0.00,
                'unpaid', '张三', _parse_date('2026-03-01')
            )
            PropertyBillDAO.create(
                'WY202603001', '京A12345', '2026-03', 350.00, 0.00,
                'unpaid', '张三', _parse_date('2026-04-01')
            )
            PropertyBillDAO.create(
                'WY202604001', '京A12345', '2026-04', 350.00, 0.00,
                'unpaid', '张三', _parse_date('2026-05-01')
            )
            PropertyBillDAO.create(
                'WY202605001', '京A12345', '2026-05', 350.00, 0.00,
                'unpaid', '张三', _parse_date('2026-06-01')
            )
            PropertyBillDAO.create(
                'WY202606001', '京A12345', '2026-06', 350.00, 0.00,
                'unpaid', '张三', _parse_date('2026-07-01')
            )

            PropertyBillDAO.create(
                'WY202601002', '京B67890', '2026-01', 420.00, 420.00,
                'paid', '李四', _parse_date('2026-02-01')
            )
            PropertyBillDAO.create(
                'WY202602002', '京B67890', '2026-02', 420.00, 420.00,
                'paid', '李四', _parse_date('2026-03-01')
            )
            PropertyBillDAO.create(
                'WY202603002', '京B67890', '2026-03', 420.00, 420.00,
                'paid', '李四', _parse_date('2026-04-01')
            )
            PropertyBillDAO.create(
                'WY202604002', '京B67890', '2026-04', 420.00, 420.00,
                'paid', '李四', _parse_date('2026-05-01')
            )
            print('物业费账单测试数据初始化成功')

        print('数据库初始化完成！')


if __name__ == '__main__':
    init_database()
