import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Talons(SqlAlchemyBase):
    __tablename__ = 'talons'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    form = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    milk = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    dinner = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    mal_ob = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    af_dinner = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now())


class Forms(SqlAlchemyBase):
    __tablename__ = 'forms'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    form = sqlalchemy.Column(sqlalchemy.String, nullable=True)