import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db
from app.dao import RateConfigDAO, GateDeviceDAO, VehicleDAO


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

        print('数据库初始化完成！')


if __name__ == '__main__':
    init_database()
