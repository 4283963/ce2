import time
import logging
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError, OperationalError, TimeoutError
from app.models import db

logger = logging.getLogger(__name__)


def with_db_retry(max_retries=3, retry_interval=0.1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except OperationalError as e:
                    last_exception = e
                    logger.warning(
                        f'Database operation failed (attempt {attempt + 1}/{max_retries}): {str(e)}'
                    )
                    db.session.rollback()
                    if attempt < max_retries - 1:
                        time.sleep(retry_interval * (attempt + 1))
                except TimeoutError as e:
                    last_exception = e
                    logger.warning(
                        f'Database timeout (attempt {attempt + 1}/{max_retries}): {str(e)}'
                    )
                    db.session.rollback()
                    if attempt < max_retries - 1:
                        time.sleep(retry_interval * (attempt + 1))
                except SQLAlchemyError as e:
                    db.session.rollback()
                    logger.error(f'Database error in {func.__name__}: {str(e)}')
                    raise
            if last_exception:
                logger.error(
                    f'Database operation failed after {max_retries} attempts: {str(last_exception)}'
                )
                raise last_exception
        return wrapper
    return decorator


def db_commit():
    try:
        db.session.commit()
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f'Database commit failed: {str(e)}')
        raise


def db_rollback():
    try:
        db.session.rollback()
    except Exception as e:
        logger.error(f'Database rollback failed: {str(e)}')


def safe_db_operation(operation_func, *args, **kwargs):
    try:
        result = operation_func(*args, **kwargs)
        return result
    except SQLAlchemyError:
        db.session.rollback()
        raise
