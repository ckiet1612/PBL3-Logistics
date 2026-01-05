# models/route.py
from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from models.base import Base


class Route(Base):
    """Route model for shipping routes between provinces."""
    __tablename__ = 'routes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    origin_province = Column(String(50), nullable=False)  # Tỉnh xuất phát
    dest_province = Column(String(50), nullable=False)    # Tỉnh đích
    distance_km = Column(Float, default=0.0)              # Khoảng cách (km)
    est_hours = Column(Float, default=0.0)                # Thời gian dự kiến (giờ)
    base_price = Column(Float, default=0.0)               # Giá cước cơ bản (VND)
    price_per_kg = Column(Float, default=5000.0)          # Phí theo cân (VND/kg)
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<Route({self.origin_province} → {self.dest_province}, {self.distance_km}km)>"
    
    def get_route_display(self):
        """Get display string for route."""
        return f"{self.origin_province} → {self.dest_province}"
    
    def calculate_shipping_cost(self, weight_kg):
        """Calculate shipping cost based on weight."""
        return self.base_price + (weight_kg * self.price_per_kg)
