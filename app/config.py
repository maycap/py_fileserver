# coding: utf-8
import os


class Config(object):

    DEBUG = True
    DATABASE_PATH = os.path.join(os.getcwd(), 'data/foo.db')
    DATABASE_URI = 'sqlite:///{}'.format(DATABASE_PATH)
    LOG_PATH = os.path.join(os.getcwd(), 'data')
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'data')
    ALLOWED_EXTENSIONS = set(['log', 'tar', 'gz', 'hprof', 'pdf'])
    APP_TOKEN = 'hcDkK99+Sk5US/Xoeg3Fmb4t0wagzdUBDi2HrJ93kB/IWDtEv75LIg'

class ProductionConfig(Config):
    DEBUG = False
    LOG_PATH = '/home/admin/output/py-fileserver/logs'
    DATABASE_PATH = '/home/admin/data/foo.db'
    UPLOAD_FOLDER = '/home/admin/data'

configs = {
    'DEFAULT': Config,
    'PRODUCTION': ProductionConfig
}