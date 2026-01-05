# models/warehouse.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from models.base import Base


class Warehouse(Base):
    """Warehouse model for storing warehouse information."""
    __tablename__ = 'warehouses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    address = Column(Text)
    province = Column(String(50))
    capacity = Column(Integer, default=100)  # Maximum number of orders
    status = Column(String(20), default='active')  # active, maintenance, closed
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<Warehouse(id={self.id}, name={self.name}, status={self.status})>"
    
    def get_status_display(self):
        """Get Vietnamese display for status."""
        status_map = {
            'active': 'Hoạt động',
            'maintenance': 'Bảo trì',
            'closed': 'Đóng cửa'
        }
        return status_map.get(self.status, self.status)


class OrderWarehouseHistory(Base):
    """Track order movements between warehouses."""
    __tablename__ = 'order_warehouse_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'), nullable=False)
    action = Column(String(20))  # 'in' (nhập kho) or 'out' (xuất kho)
    note = Column(Text)
    timestamp = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<OrderWarehouseHistory(order={self.order_id}, warehouse={self.warehouse_id}, action={self.action})>"
