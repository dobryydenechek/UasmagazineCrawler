from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY, JSON
from datetime import datetime
import pytz

import settings


def db_connect():
    return create_engine(URL(**settings.DATABASE))


DeclarativeBase = declarative_base()


def create_tables(engine):
    DeclarativeBase.metadata.create_all(engine)


def time_now():
    return datetime.now(tz=pytz.timezone("Europe/Moscow"))


documents_files_table = Table('core_document_files', DeclarativeBase.metadata,
                              Column('document_id', Integer, ForeignKey('core_document.id')),
                              Column('file_id', Integer, ForeignKey('core_file.id'))
                              )


class Spider(DeclarativeBase):
    __tablename__ = 'core_spider'

    id = Column(Integer, primary_key=True)
    name = Column('name', String)
    last_run_at = Column('last_run_at', DateTime, nullable=True, default=time_now)
    last_session_key = Column('last_session_key', String)


class Document(DeclarativeBase):
    __tablename__ = 'core_document'

    id = Column(Integer, primary_key=True)
    spider_id = Column(Integer, ForeignKey('core_spider.id'))
    url = Column('url', String, nullable=True)
    author = Column('author', String, nullable=True)
    created_date = Column('created_date', DateTime, nullable=True, default=time_now)
    published_date = Column('published_date', DateTime, nullable=True)
    title = Column('title', String, nullable=True)
    text = Column('text', String, nullable=True)
    files = relationship('File', uselist=True, secondary=documents_files_table, back_populates='documents')
    file_urls = Column('file_urls', ARRAY(String), nullable=True)
    image_urls = Column('image_urls', ARRAY(String), nullable=True)
    youtube_urls = Column('youtube_urls', ARRAY(String), nullable=True)
    soundcloud_urls = Column('soundcloud_urls', ARRAY(String), nullable=True)
    info_id = Column(Integer, ForeignKey('core_additionalinformation.id'))

    info = relationship('AdditionalInformation', back_populates='document')


class File(DeclarativeBase):
    __tablename__ = 'core_file'

    id = Column(Integer, primary_key=True)
    type = Column('type', String, default='file')
    spider_id = Column(Integer, ForeignKey('core_spider.id'))
    url = Column('url', String, nullable=True)
    path = Column('path', String, nullable=True)
    checksum = Column('checksum', String, nullable=True)
    documents = relationship('Document', secondary=documents_files_table, back_populates='files')
    created_date = Column('created_date', DateTime, nullable=True, default=time_now)
    info_id = Column(Integer, ForeignKey('core_additionalinformation.id'))
    info = relationship('AdditionalInformation', back_populates='file')


class Error(DeclarativeBase):
    __tablename__ = 'core_error'

    id = Column(Integer, primary_key=True)
    spider_id = Column(Integer, ForeignKey('core_spider.id'))
    url = Column('url', String, nullable=True)
    exception = Column('exception', String, nullable=True)
    traceback = Column('traceback', String, nullable=True)
    response = Column('response', JSON, nullable=True)
    created_date = Column('created_date', DateTime, nullable=True, default=time_now)


class AdditionalInformation(DeclarativeBase):
    __tablename__ = 'core_additionalinformation'

    id = Column(Integer, primary_key=True)
    spider_id = Column(Integer, ForeignKey('core_spider.id'))
    is_file = Column('is_file', Boolean, default=False)
    size = Column('size', Integer, default=0)
    session_key = Column('session_key', String)
    created_date = Column('created_date', DateTime, nullable=True, default=time_now)

    document = relationship('Document', uselist=False, back_populates='info')
    file = relationship('File', uselist=False, back_populates='info')
