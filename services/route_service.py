# services/route_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from database.db_connection import SessionLocal
from models.route import Route
from models.order import Order


class RouteService:
    """Service for route CRUD and shipping cost calculation."""
    
    def get_all_routes(self):
        """Get all routes."""
        session: Session = SessionLocal()
        try:
            return session.query(Route).order_by(Route.origin_province, Route.dest_province).all()
        finally:
            session.close()
    
    def get_route_by_id(self, route_id):
        """Get route by ID."""
        session: Session = SessionLocal()
        try:
            return session.query(Route).filter(Route.id == route_id).first()
        finally:
            session.close()
    
    def find_route(self, origin, dest):
        """Find route by origin and destination."""
        session: Session = SessionLocal()
        try:
            return session.query(Route).filter(
                and_(Route.origin_province == origin, Route.dest_province == dest)
            ).first()
        finally:
            session.close()
    
    def create_route(self, data):
        """Create new route."""
        session: Session = SessionLocal()
        try:
            # Check if route already exists
            existing = session.query(Route).filter(
                and_(
                    Route.origin_province == data.get('origin_province'),
                    Route.dest_province == data.get('dest_province')
                )
            ).first()
            
            if existing:
                return False, "Tuyến đường này đã tồn tại"
            
            route = Route(
                origin_province=data.get('origin_province'),
                dest_province=data.get('dest_province'),
                distance_km=data.get('distance_km', 0),
                est_hours=data.get('est_hours', 0),
                base_price=data.get('base_price', 0),
                price_per_kg=data.get('price_per_kg', 5000)
            )
            session.add(route)
            session.commit()
            return True, "Thêm tuyến đường thành công"
        except Exception as e:
            session.rollback()
            return False, f"Lỗi: {e}"
        finally:
            session.close()
    
    def update_route(self, route_id, data):
        """Update route."""
        session: Session = SessionLocal()
        try:
            route = session.query(Route).filter(Route.id == route_id).first()
            if route:
                route.origin_province = data.get('origin_province', route.origin_province)
                route.dest_province = data.get('dest_province', route.dest_province)
                route.distance_km = data.get('distance_km', route.distance_km)
                route.est_hours = data.get('est_hours', route.est_hours)
                route.base_price = data.get('base_price', route.base_price)
                route.price_per_kg = data.get('price_per_kg', route.price_per_kg)
                session.commit()
                return True, "Cập nhật tuyến đường thành công"
            return False, "Không tìm thấy tuyến đường"
        except Exception as e:
            session.rollback()
            return False, f"Lỗi: {e}"
        finally:
            session.close()
    
    def delete_route(self, route_id):
        """Delete route."""
        session: Session = SessionLocal()
        try:
            route = session.query(Route).filter(Route.id == route_id).first()
            if route:
                session.delete(route)
                session.commit()
                return True, "Xóa tuyến đường thành công"
            return False, "Không tìm thấy tuyến đường"
        except Exception as e:
            session.rollback()
            return False, f"Lỗi: {e}"
        finally:
            session.close()
    
    def calculate_shipping_cost(self, origin, dest, weight_kg):
        """Calculate shipping cost for a route."""
        route = self.find_route(origin, dest)
        if route:
            return route.calculate_shipping_cost(weight_kg)
        # Default cost if no route found
        return weight_kg * 10000  # 10,000 VND/kg default
    
    def get_route_stats(self):
        """Get statistics for routes."""
        session: Session = SessionLocal()
        try:
            routes = session.query(Route).all()
            stats = []
            
            for route in routes:
                # Count orders on this route
                order_count = session.query(Order).filter(
                    and_(
                        Order.sender_province == route.origin_province,
                        Order.receiver_province == route.dest_province
                    )
                ).count()
                
                stats.append({
                    'route': route,
                    'order_count': order_count
                })
            
            # Sort by order_count descending
            stats.sort(key=lambda x: x['order_count'], reverse=True)
            return stats
        finally:
            session.close()
