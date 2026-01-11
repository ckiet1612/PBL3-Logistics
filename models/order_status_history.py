# models/order_status_history.py
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from models.base import Base


class OrderStatusHistory(Base):
    """Model to track order status changes over time."""
    __tablename__ = 'order_status_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    old_status = Column(String(50), nullable=True)  # Null for initial status
    new_status = Column(String(50), nullable=False)
    changed_at = Column(DateTime, default=datetime.now)
    changed_by = Column(String(100), nullable=True)  # User who made the change
    note = Column(String(500), nullable=True)

    def get_status_display(self):
        """Return Vietnamese status display."""
        status_map = {
            'New': 'Mới tạo',
            'Processing': 'Đang xử lý',
            'Shipping': 'Đang giao',
            'Delivered': 'Đã giao',
            'Cancelled': 'Đã huỷ'
        }
        return status_map.get(self.new_status, self.new_status)

    def get_status_icon(self):
        """Return icon for status."""
        icon_map = {
            'New': '🆕',
            'Processing': '⏳',
            'Shipping': '🚚',
            'Delivered': '✅',
            'Cancelled': '❌'
        }
        return icon_map.get(self.new_status, '📋')
