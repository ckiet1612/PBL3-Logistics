# models/base.py
from sqlalchemy.orm import DeclarativeBase

# This Class Base will be inherited by other Models.
class Base(DeclarativeBase):
    pass