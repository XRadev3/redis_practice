import os
import logging
import functools


@functools.lru_cache()
def app_config():
    configuration = {
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'the very many much wow secret key'),
        'FLASK_ENV': os.environ.get('FLASK_ENV', 'development'),
        'FLASK_DEBUG': os.environ.get('FLASK_DEBUG', '1')
    }
    return configuration


@functools.lru_cache()
def get_secret_key():
    configuration = app_config()

    return configuration['SECRET_KEY']
