import sqlalchemy
from .db_session import SqlAlchemyBase


class Form(SqlAlchemyBase):
    __tablename__ = 'forms'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    form = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    school = sqlalchemy.Column(sqlalchemy.String, nullable=True)