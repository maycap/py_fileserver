# coding: utf-8

import hashlib
import logging
from contextlib import contextmanager
from functools import wraps

import os
import time
from flask import request
from flask_restful import abort
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from app.config import configs


def get_config():
    key = os.getenv('FILE_ENV') or 'default'
    key = key.upper()
    return configs[key]

Myconfig = get_config()

def random_sha():
    now = time.time()
    sha1 = hashlib.sha1(str(now))
    return sha1.hexdigest()


some_engine = create_engine(Myconfig.DATABASE_URI, echo=False)
Session = sessionmaker(bind=some_engine, autoflush=False, expire_on_commit=False)

cx = some_engine.connect()

@contextmanager
def get_session():
    try:
        s = Session()
        s.expire_on_commit = False
        yield s
    except:
        s.rollback()
        raise
    finally:
        s.close()


def lock_access(func):
    @wraps(func)

    def func_wrapper(*args, **kwargs):
        file_token = kwargs.get('file_token', None)
        from app.models import FileManager
        fm = FileManager()
        if fm.doned_download(file_token):
            return func(*args, **kwargs)
        abort(403)
    return func_wrapper

def check_manage(func):
    @wraps(func)

    def func_wrappers(*args, **kwargs):
        token = request.headers.get('token')
        if token != Myconfig.APP_TOKEN:
            abort(403)
        return func(*args, **kwargs)
    return func_wrappers

def check_remote(func):
    @wraps(func)

    def func_wrappers(*args, **kwargs):
        dst_ip = request.remote_addr
        file_token = kwargs.get('file_token', None)
        from app.models import FileManager
        fm = FileManager()
        rule_ip = fm.get_upload(file_token)
        if not rule_ip:
            abort(403, message=u'无效token,请重新申请')
        if dst_ip != rule_ip:
            abort(403, message=u'使用地点：{} 与申请地点为:{} 不同，上传被阻止，token已被禁用'.format(dst_ip, rule_ip))
        return func(*args, **kwargs)
    return func_wrappers

def get_logger(name='web'):
    # create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # file handler
    log_path = os.path.join(Myconfig.LOG_PATH, '{}.log'.format(name))
    fh = logging.FileHandler(log_path)
    fh.setLevel(logging.INFO)

    # create formatter
    fmt = "%(asctime)-15s %(levelname)s %(filename)s:%(lineno)d %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt, datefmt)

    # add handler and formatter to logger
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


def get_md5(fd):
    count = hashlib.md5()
    for line in fd.xreadlines():
        count.update(line)
    fd.seek(0)
    return count.hexdigest()

