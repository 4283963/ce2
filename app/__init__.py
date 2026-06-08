from flask import Flask, jsonify
from sqlalchemy import event
from app.config import Config
from app.models import db


def _setup_sqlite_pragmas(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute('PRAGMA journal_mode=WAL')
    cursor.execute('PRAGMA busy_timeout=30000')
    cursor.execute('PRAGMA synchronous=NORMAL')
    cursor.close()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    with app.app_context():
        engine = db.engine
        if 'sqlite' in str(engine.url):
            event.listen(engine, 'connect', _setup_sqlite_pragmas)

    from app.controllers import gate_bp, billing_bp, payment_bp, vehicle_bp
    app.register_blueprint(gate_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(vehicle_bp)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        if exception is not None:
            db.session.rollback()
        db.session.remove()

    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'status': 'ok',
                'service': 'parking-management-system'
            }
        }), 200

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'code': 404,
            'message': '接口不存在',
            'data': None
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': '服务器内部错误',
            'data': None
        }), 500

    return app
