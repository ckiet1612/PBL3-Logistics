# models/order.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from datetime import datetime
from models.base import Base

class Order(Base):
    __tablename__ = 'orders'

    # 1. Identification
    id = Column(Integer, primary_key=True, autoincrement=True)
    tracking_code = Column(String(50), unique=True, nullable=False)
    order_type = Column(String(20), default='domestic')  # 'domestic' or 'international'

    # 2. Sender Information
    sender_name = Column(String(100))
    sender_phone = Column(String(20))
    sender_email = Column(String(100))
    sender_address = Column(Text)
    sender_province = Column(String(50))  # Tỉnh/thành gửi
    sender_ward = Column(String(100))  # Xã/phường gửi

    # 3. Receiver Information
    receiver_name = Column(String(100))
    receiver_phone = Column(String(20))
    receiver_email = Column(String(100))
    receiver_address = Column(Text)
    receiver_province = Column(String(50))  # Tỉnh/thành nhận
    receiver_ward = Column(String(100))  # Xã/phường nhận

    # Warehouse reference
    current_warehouse_id = Column(Integer, ForeignKey('warehouses.id'), nullable=True)

    # 4. Package Information
    item_name = Column(String(200))  # Tên/Mô tả hàng hoá
    item_type = Column(String(20), default='normal')  # 'normal', 'fragile', 'frozen', 'dangerous'
    package_count = Column(Integer, default=1)  # Số kiện
    weight = Column(Float, default=0.0)  # kg
    dimensions = Column(String(50))  # Kích thước DxRxC cm

    # 5. Service & Delivery
    service_type = Column(String(20), default='standard')  # 'standard', 'express', 'urgent'
    delivery_note = Column(Text)  # Ghi chú giao hàng

    # 6. Payment & COD
    payment_type = Column(String(20), default='sender')  # 'sender' or 'receiver'
    shipping_cost = Column(Float, default=0.0)  # Phí vận chuyển
    has_cod = Column(Boolean, default=False)  # Có COD không
    cod_amount = Column(Float, default=0.0)  # Số tiền thu hộ

    # 7. Status & Image
    status = Column(String(50), default='New')
    image_path = Column(String(255), nullable=True)

    # 8. Time
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Order(id={self.id}, code={self.tracking_code}, status={self.status})>"

    def get_total_cost(self):
        """Get total cost including COD if applicable."""
        total = self.shipping_cost or 0.0
        if self.has_cod:
            total += self.cod_amount or 0.0
        return total

    def get_route_summary(self):
        """Get sender -> receiver province summary."""
        sender = self.sender_province or "N/A"
        receiver = self.receiver_province or "N/A"
        return f"{sender} → {receiver}"

    def get_package_summary(self):
        """Get package count and weight summary."""
        count = self.package_count or 1
        weight = self.weight or 0.0
        return f"{count} kiện / {weight:.1f} kg"
