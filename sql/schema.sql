CREATE TABLE IF NOT EXISTS gate_devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_code VARCHAR(50) NOT NULL UNIQUE,
    device_name VARCHAR(100) NOT NULL,
    location VARCHAR(200),
    status INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plate_number VARCHAR(20) NOT NULL UNIQUE,
    vehicle_type VARCHAR(20) NOT NULL DEFAULT 'visitor',
    owner_name VARCHAR(50),
    owner_phone VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vehicle_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plate_number VARCHAR(20) NOT NULL,
    gate_id INTEGER,
    direction VARCHAR(10) NOT NULL,
    record_time DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_plate_number (plate_number),
    INDEX idx_record_time (record_time)
);

CREATE TABLE IF NOT EXISTS parking_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_no VARCHAR(32) NOT NULL UNIQUE,
    plate_number VARCHAR(20) NOT NULL,
    entry_time DATETIME NOT NULL,
    exit_time DATETIME,
    duration_minutes INTEGER DEFAULT 0,
    amount DECIMAL(10,2) DEFAULT 0.00,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_plate_number (plate_number),
    INDEX idx_status (status)
);

CREATE TABLE IF NOT EXISTS payment_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_no VARCHAR(32) NOT NULL UNIQUE,
    order_id INTEGER NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    pay_method VARCHAR(20) NOT NULL,
    pay_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    pay_time DATETIME,
    third_party_trade_no VARCHAR(64),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_order_id (order_id),
    INDEX idx_pay_status (pay_status)
);

CREATE TABLE IF NOT EXISTS rate_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rate_type VARCHAR(20) NOT NULL DEFAULT 'visitor',
    free_minutes INTEGER DEFAULT 30,
    first_hour_price DECIMAL(10,2) DEFAULT 5.00,
    per_hour_price DECIMAL(10,2) DEFAULT 3.00,
    max_daily_price DECIMAL(10,2) DEFAULT 50.00,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO rate_configs (id, rate_type, free_minutes, first_hour_price, per_hour_price, max_daily_price)
VALUES (1, 'visitor', 30, 5.00, 3.00, 50.00);

INSERT OR IGNORE INTO gate_devices (device_code, device_name, location, status)
VALUES 
('GATE-001', '东门入口', '小区东门', 1),
('GATE-002', '东门出口', '小区东门', 1),
('GATE-003', '西门入口', '小区西门', 1),
('GATE-004', '西门出口', '小区西门', 1);

INSERT OR IGNORE INTO vehicles (plate_number, vehicle_type, owner_name, owner_phone)
VALUES 
('京A12345', 'resident', '张三', '13800138001'),
('京B67890', 'resident', '李四', '13800138002');
