import logging.config

# init logger
try:
    logging.config.fileConfig('logging.conf')
except IOError as io_err:
    dirname = os.path.dirname(io_err.filename)
    os.makedirs(dirname)
    logging.config.fileConfig('logging.conf')
except:
    logging.exception("config logging failed")
    pass

logger = logging.getLogger('root')

