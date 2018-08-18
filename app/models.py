# coding:utf-8
from datetime import datetime
from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean
from sqlalchemy.ext.declarative import declarative_base

from helper import random_sha, get_session

Base = declarative_base()


class FileToken(Base):
    """file token"""

    __tablename__ = 'file_token'

    id = Column(Integer, primary_key=True)
    user = Column(String(64))
    dst_ip = Column(String(64))
    filename = Column(String(128))
    file_token = Column(String(128))
    upload_counter = Column(Integer)
    download_counter = Column(Integer)
    alive = Column(Boolean)
    gmt_create = Column(TIMESTAMP, default=datetime.now)
    gmt_modify = Column(TIMESTAMP, default=datetime.now)


    def __unicode__(self):
        format_info = u"file_token info: <id={0},user={1},filename={2}"
        info = format_info.format(
            self.id, self.user, self.filename)
        return info

    def __repr__(self):
        return self.__unicode__().encode('utf-8')

# Base.metadata.create_all(some_engine)

class FileManager(object):

    def __init__(self):
        pass

    def create(self, user, dst_ip):
        with get_session() as ss:
            file_token = random_sha()
            file = FileToken(
                user=user,
                dst_ip=dst_ip,
                file_token=file_token,
                upload_counter=1,
                download_counter=-1,
                alive=False,
            )
            ss.add(file)
            ss.commit()
            return file_token

    def update(self, file_token, name):
        with get_session() as ss:
            query = ss.query(FileToken).filter(FileToken.file_token==file_token).first()
            query.filename = name
            query.download_counter = 1
            ss.add(query)
            ss.commit()
            return True

    def update_counter(self, file_token, download_counter):
        """
        更新计数
        :param file_token:
        :param download_counter:
        :return:
        """
        with get_session() as ss:
            query = ss.query(FileToken).filter(FileToken.file_token==file_token).first()
            if not query:
                return False,'file_token not found!'
            query.download_counter = abs(download_counter)
            ss.add(query)
            ss.commit()
            return True, 'ok'


    def get_upload(self, file_token):
        with get_session() as ss:
            query = ss.query(FileToken).filter(
                FileToken.file_token == file_token,
                FileToken.alive == False,
                FileToken.upload_counter > 0
            ).first()
            if not query:
                return False
            query.upload_counter -= 1
            ss.add(query)
            ss.commit()
            return query.dst_ip

    def get_download(self, file_token):
        with get_session() as ss:
            query = ss.query(FileToken).filter(
                FileToken.file_token == file_token,
                FileToken.alive == False,
                FileToken.download_counter > 0
            ).first()
            if not query:
                return False
            query.download_counter -= 1
            query.alive = True
            ss.add(query)
            ss.commit()
            return query.filename

    def doned_download(self, file_token):
        with get_session() as ss:
            query = ss.query(FileToken).filter(
                FileToken.file_token == file_token,
                FileToken.alive == True
            ).first()
            if query:
                query.alive = False
                ss.add(query)
                ss.commit()
                return True
            return False
