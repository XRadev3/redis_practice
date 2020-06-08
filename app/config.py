import os
import logging
import functools

from app.cache import Cache

cache = Cache()


@functools.lru_cache()
def app_data():
    configuration = {
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'the very many much wow secret key'),
        'FLASK_ENV': os.environ.get('FLASK_ENV', 'development'),
        'FLASK_DEBUG': os.environ.get('FLASK_DEBUG', '1'),
        'LOGGING': False
    }
    return configuration


@functools.lru_cache()
def get_app_conf():
    application_data = app_data()
    app_conf = {
        'SECRET_KEY': application_data['SECRET_KEY'],
        'FLASK_ENV': application_data['FLASK_ENV'],
        'FLASK_DEBUG': application_data['FLASK_DEBUG']
    }
    set_logging()

    return app_conf


@functools.lru_cache()
def get_secret_key():
    configuration = app_data()

    return configuration['SECRET_KEY']


@functools.lru_cache()
def set_logging():
    configuration = app_data()
    if not configuration['LOGGING']:
        try:
            path = os.getcwd() + '/../app_log.log'
            logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                                datefmt='%Y-%m-%d:%H:%M:%S',
                                filename=path,
                                level=logging.DEBUG)
            configuration['LOGGING'] = True

        except Exception as message:
            return False

    return True
