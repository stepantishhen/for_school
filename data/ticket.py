from datetime import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Ticket(SqlAlchemyBase):
    __tablename__ = 'talons'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    milk = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    dinner = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    low_income = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    snack = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    school = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    form_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.utcnow)
