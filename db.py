import hashlib
import datetime

from sqlalchemy import create_engine, Column, Integer, String, Text, Time, ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DB = 'mysql://root@localhost/bookworm'


Base = declarative_base()

class File(Base):

    __tablename__ = 'files'

    fingerprint = Column(String(255), primary_key=True)
    format      = Column(String(255))
    size        = Column(Integer)


class Path(Base):

    __tablename__ = 'paths'

    # id is md5(path), since primary key can't get longer than 255
    id        = Column(String(255), primary_key=True)
    path      = Column(Text) #FIXME: add index
    created_t = Column(Time)
    file_id   = Column(String(255), ForeignKey('files.fingerprint'))

    def __str__(self):
        return '\t'.join([self.file_id, self.path])


'''
class Book(Base):

    __tablename__ = 'books'

    book_id   = Column(String(255), primary_key=True)
    title     = Column(String(255))
    author    = Column(String(255))
    num_pages = Column(Integer)
    pub_year  = Column(String(64))
    isbn      = Column(String(64))
    #keywords, tags, catagory


class Page(Base):

    __tablename__ = 'pages'

    book_id = Column(String(255), ForeignKey('books.book_id'), primary_key=True)
    page_no = Column(Integer, primary_key=True, autoincrement=False)
    content = Column(Text)
'''


class API(object):

    _engine = None
    _Session = None

    @property
    def engine(self):
        if self._engine is None:
            self._engine = create_engine(DB, echo=False)
        return self._engine

    @property
    def Session(self):
        if self._Session is None:
            self._Session = sessionmaker(bind=self.engine)
        return self._Session

    def create_db(self):
        Base.metadata.create_all(self.engine)

    def get_paths(self):
        session = self.Session()
        return session.query(Path)

    def add_filedata(self, many):
        file_records = []
        path_records = []

        session = self.Session()
        for fdata in many:
            cnt = session.query(File).filter_by(fingerprint=fdata.fingerprint).count()
            if cnt == 0:
                file_records.append(File(
                    fingerprint=fdata.fingerprint,
                    format=fdata.format,
                    size=fdata.size,
                    ))
            path_records.append(Path(
                id=hashlib.md5(fdata.path).hexdigest(),
                path=fdata.path,
                created_t=datetime.datetime.now(),
                file_id=fdata.fingerprint,
                ))

        session.add_all(file_records)
        # need commit here, since path has a foreign key straint on file
        session.commit() 

        session.add_all(path_records)
        session.commit()


api = API()

 
if __name__ == '__main__':
    api.create_db()
