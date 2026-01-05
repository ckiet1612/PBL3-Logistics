# services/warehouse_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.db_connection import SessionLocal
from models.warehouse import Warehouse, OrderWarehouseHistory
from models.order import Order
from datetime import datetime


class WarehouseService:
    """Service for warehouse CRUD operations."""
    
    def get_all_warehouses(self):
        """Get all warehouses."""
        session: Session = SessionLocal()
        try:
            return session.query(Warehouse).order_by(Warehouse.name).all()
        finally:
            session.close()
    
    def get_warehouse_by_id(self, warehouse_id):
        """Get warehouse by ID."""
        session: Session = SessionLocal()
        try:
            return session.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
        finally:
            session.close()
    
    def create_warehouse(self, data):
        """Create new warehouse."""
        session: Session = SessionLocal()
        try:
            warehouse = Warehouse(
                name=data.get('name'),
                address=data.get('address'),
                province=data.get('province'),
                capacity=data.get('capacity', 100),
                status=data.get('status', 'active')
            )
            session.add(warehouse)
            session.commit()
            return True, "Thêm kho thành công"
        except Exception as e:
            session.rollback()
            return False, f"Lỗi: {e}"
        finally:
            session.close()
    
    def update_warehouse(self, warehouse_id, data):
        """Update warehouse."""
        session: Session = SessionLocal()
        try:
            warehouse = session.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
            if warehouse:
                warehouse.name = data.get('name', warehouse.name)
                warehouse.address = data.get('address', warehouse.address)
                warehouse.province = data.get('province', warehouse.province)
                warehouse.capacity = data.get('capacity', warehouse.capacity)
                warehouse.status = data.get('status', warehouse.status)
                session.commit()
                return True, "Cập nhật kho thành công"
            return False, "Không tìm thấy kho"
        except Exception as e:
            session.rollback()
            return False, f"Lỗi: {e}"
        finally:
            session.close()
    
    def delete_warehouse(self, warehouse_id):
        """Delete warehouse."""
        session: Session = SessionLocal()
        try:
            warehouse = session.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
            if warehouse:
                # Check if any orders are in this warehouse
                order_count = session.query(Order).filter(
                    Order.current_warehouse_id == warehouse_id
                ).count()
                if order_count > 0:
                    return False, f"Không thể xóa kho có {order_count} đơn hàng"
                
                session.delete(warehouse)
                session.commit()
                return True, "Xóa kho thành công"
            return False, "Không tìm thấy kho"
        except Exception as e:
            session.rollback()
            return False, f"Lỗi: {e}"
        finally:
            session.close()
    
    def get_warehouse_stats(self, warehouse_id):
        """Get warehouse statistics."""
        session: Session = SessionLocal()
        try:
            warehouse = session.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
            if not warehouse:
                return None
            
            # Count orders in warehouse
            order_count = session.query(Order).filter(
                Order.current_warehouse_id == warehouse_id
            ).count()
            
            # Calculate capacity percentage
            capacity_pct = (order_count / warehouse.capacity * 100) if warehouse.capacity > 0 else 0
            
            return {
                'order_count': order_count,
                'capacity': warehouse.capacity,
                'capacity_pct': round(capacity_pct, 1),
                'status': warehouse.status
            }
        finally:
            session.close()
    
    def get_orders_in_warehouse(self, warehouse_id):
        """Get all orders currently in a warehouse."""
        session: Session = SessionLocal()
        try:
            return session.query(Order).filter(
                Order.current_warehouse_id == warehouse_id
            ).all()
        finally:
            session.close()
    
    def assign_order_to_warehouse(self, order_id, warehouse_id, note=""):
        """Assign an order to a warehouse."""
        session: Session = SessionLocal()
        try:
            order = session.query(Order).filter(Order.id == order_id).first()
            if not order:
                return False, "Không tìm thấy đơn hàng"
            
            old_warehouse_id = order.current_warehouse_id
            
            # Record history if moving from another warehouse
            if old_warehouse_id and old_warehouse_id != warehouse_id:
                history_out = OrderWarehouseHistory(
                    order_id=order_id,
                    warehouse_id=old_warehouse_id,
                    action='out',
                    note=f"Chuyển đến kho ID {warehouse_id}"
                )
                session.add(history_out)
            
            # Update order warehouse
            order.current_warehouse_id = warehouse_id
            
            # Record history for new warehouse
            history_in = OrderWarehouseHistory(
                order_id=order_id,
                warehouse_id=warehouse_id,
                action='in',
                note=note or "Nhập kho"
            )
            session.add(history_in)
            
            session.commit()
            return True, "Gán đơn vào kho thành công"
        except Exception as e:
            session.rollback()
            return False, f"Lỗi: {e}"
        finally:
            session.close()
    
    def get_order_warehouse_history(self, order_id):
        """Get warehouse movement history for an order."""
        session: Session = SessionLocal()
        try:
            return session.query(OrderWarehouseHistory).filter(
                OrderWarehouseHistory.order_id == order_id
            ).order_by(OrderWarehouseHistory.timestamp.desc()).all()
        finally:
            session.close()
