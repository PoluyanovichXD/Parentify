import sqlalchemy, os
from sqlalchemy                     import create_engine, or_, and_, event
from sqlalchemy.orm                 import sessionmaker, scoped_session
from sqlalchemy.ext.declarative     import declarative_base
from django.conf                    import settings



DATABASE_CONNECTION_STRING = os.getenv('DATABASE_CONNECTION_STRING', 'postgresql+psycopg2://postgres:postgres@localhost/starkonet_web_develop')

if DATABASE_CONNECTION_STRING.startswith('sqlite://'):
    engine = create_engine(DATABASE_CONNECTION_STRING)
else:
    engine = create_engine(DATABASE_CONNECTION_STRING, echo = False, pool_size=20, max_overflow=0)

Orm = sessionmaker(bind=engine)
session = scoped_session(Orm)

Base = declarative_base()
Base.query = session.query_property()
Base.url_key = property(lambda self: getattr(self, self.url_key_name) )