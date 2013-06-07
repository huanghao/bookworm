from sqlalchemy import create_engine, Column, Integer, String, Text, Time, ForeignKey
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
    path      = Column(Text)
    created_t = Column(Time)
    file_id   = Column(String(255), ForeignKey('files.fingerprint'))


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

    @property
    def engine(self):
        if self._engine is None:
            self._engine = create_engine(DB, echo=True)
        return self._engine

    def create_db(self):
        Base.metadata.create_all(self.engine)

api = API()

 
if __name__ == '__main__':
    api.create_db()
