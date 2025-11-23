import sqlalchemy, os
from sqlalchemy                     import create_engine, or_, and_, event
from sqlalchemy.orm                 import sessionmaker, scoped_session
from sqlalchemy.ext.declarative     import declarative_base
from sqlalchemy.inspection import inspect
from django.conf                    import settings



DATABASE_CONNECTION_STRING = os.getenv('DATABASE_CONNECTION_STRING', 'postgresql+psycopg2://postgres:postgres@localhost:5432/parentify_db')

if DATABASE_CONNECTION_STRING.startswith('sqlite://'):
    engine = create_engine(DATABASE_CONNECTION_STRING)
else:
    engine = create_engine(DATABASE_CONNECTION_STRING, echo = False, pool_size=20, max_overflow=0)

Orm = sessionmaker(bind=engine)
session = scoped_session(Orm)

Base = declarative_base()
Base.query = session.query_property()
Base.url_key = property(lambda self: getattr(self, self.url_key_name) )
Base.url_key_name = 'id'
Base.get_type = lambda self, name: 'Column' if name in inspect(self.__class__ if hasattr(self, '__class__') else self).columns else 'Relationship' if name in inspect(self.__class__ if hasattr(self, '__class__') else self).relationships else None
Base.is_column = lambda self, name: self.get_type(name)=='Column'
Base.is_relationship = lambda self, name: self.get_type(name)=='Relationship'
Base.__table_args__ = {'extend_existing': True}