import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///parking_system.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'max_overflow': 30,
        'pool_timeout': 30,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }
    SQLALCHEMY_COMMIT_ON_TEARDOWN = False

    FREE_PARKING_MINUTES = 30
    FIRST_HOUR_PRICE = 5.0
    PER_HOUR_PRICE = 3.0
    MAX_DAILY_PRICE = 50.0

    WXPAY_MOCK = True
    ALIPAY_MOCK = True

    DB_RETRY_TIMES = 3
    DB_RETRY_INTERVAL = 0.1
