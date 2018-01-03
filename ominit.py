import os.path

try:
    import flask
except ImportError:
    print('No flask')
    _install_flask = """"""

import logging

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] > %(funcName)s > %(levelname)s %(message)s',
                datefmt='%Y%b%d_%H%M%S',
                filename='om.log',
                filemode='a')

def log_info(message):
    logging.info(message)

def log_debug(message):
    logging.debug(message)

def log_error(message):
    logging.error(message)