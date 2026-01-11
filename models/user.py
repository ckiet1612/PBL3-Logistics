# models/user.py
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
from models.base import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), default='staff')  # 'admin' or 'staff'
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"

    def is_admin(self):
        """Check if user has admin privileges."""
        return self.role == 'admin'
