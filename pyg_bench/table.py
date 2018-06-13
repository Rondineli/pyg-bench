from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()


class Films(Base):
    __tablename__ = 'films'
    id = Column(Integer, primary_key=True)
    code = Column(String)
    title = Column(String)
    did = Column(Integer)
    kind = Column(String)

    def __repr__(self):
        return "Table Films: <{}>".format(self.id)
