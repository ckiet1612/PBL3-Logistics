# services/order_service.py
from sqlalchemy.orm import Session
from database.db_connection import SessionLocal
from models.order import Order

class OrderService:
    def __init__(self):
        pass

    def create_order(self, data: dict):
        """
        Create a new order and save it to the database.
        :param data: Dictionary containing order details
        :return: (success, message, order_id)
        """
        session: Session = SessionLocal()
        try:
            new_order = Order(
                tracking_code=data.get("tracking_code"),
                order_type=data.get("order_type", "domestic"),
                sender_name=data.get("sender_name"),
                sender_phone=data.get("sender_phone"),
                sender_email=data.get("sender_email"),
                sender_address=data.get("sender_address"),
                sender_province=data.get("sender_province"),
                sender_ward=data.get("sender_ward"),
                receiver_name=data.get("receiver_name"),
                receiver_phone=data.get("receiver_phone"),
                receiver_email=data.get("receiver_email"),
                receiver_address=data.get("receiver_address"),
                receiver_province=data.get("receiver_province"),
                receiver_ward=data.get("receiver_ward"),
                current_warehouse_id=data.get("current_warehouse_id"),
                item_name=data.get("item_name"),
                item_type=data.get("item_type", "normal"),
                package_count=int(data.get("package_count", 1)),
                weight=float(data.get("weight", 0.0)),
                dimensions=data.get("dimensions"),
                service_type=data.get("service_type", "standard"),
                delivery_note=data.get("delivery_note"),
                payment_type=data.get("payment_type", "sender"),
                shipping_cost=float(data.get("shipping_cost", 0.0)),
                has_cod=data.get("has_cod", False),
                cod_amount=float(data.get("cod_amount", 0.0)),
                status=data.get("status", "New")
            )
            session.add(new_order)
            session.commit()
            order_id = new_order.id
            return True, "Order added successfully", order_id
        except Exception as e:
            session.rollback()
            return False, f"Error adding order: {str(e)}", None
        finally:
            session.close()

    def get_all_orders(self):
        """
        Retrieve all orders from the database.
        """
        session: Session = SessionLocal()
        try:
            orders = session.query(Order).all()
            return orders
        except Exception as e:
            print(f"Error fetching orders: {e}")
            return []
        finally:
            session.close()

    def order_to_dict(self, order):
        """Convert Order object to dict for undo/redo storage."""
        if not order:
            return None
        if isinstance(order, dict):
            return order
        return {
            'id': order.id,
            'tracking_code': order.tracking_code,
            'order_type': order.order_type,
            'sender_name': order.sender_name,
            'sender_phone': order.sender_phone,
            'sender_email': order.sender_email,
            'sender_address': order.sender_address,
            'sender_province': order.sender_province,
            'sender_ward': order.sender_ward,
            'receiver_name': order.receiver_name,
            'receiver_phone': order.receiver_phone,
            'receiver_email': order.receiver_email,
            'receiver_address': order.receiver_address,
            'receiver_province': order.receiver_province,
            'receiver_ward': order.receiver_ward,
            'current_warehouse_id': order.current_warehouse_id,
            'item_name': order.item_name,
            'item_type': order.item_type,
            'package_count': order.package_count,
            'weight': order.weight,
            'dimensions': order.dimensions,
            'service_type': order.service_type,
            'delivery_note': order.delivery_note,
            'payment_type': order.payment_type,
            'shipping_cost': order.shipping_cost,
            'has_cod': order.has_cod,
            'cod_amount': order.cod_amount,
            'status': order.status
        }

    def search_orders(self, query: str):
        """
        Search orders by multiple fields.
        :param query: Search keyword
        :return: List of matching orders
        """
        session: Session = SessionLocal()
        try:
            if not query or not query.strip():
                return self.get_all_orders()

            search_pattern = f"%{query.strip()}%"

            orders = session.query(Order).filter(
                (Order.id.like(search_pattern)) |
                (Order.sender_name.ilike(search_pattern)) |
                (Order.receiver_name.ilike(search_pattern)) |
                (Order.sender_phone.ilike(search_pattern)) |
                (Order.receiver_phone.ilike(search_pattern)) |
                (Order.sender_address.ilike(search_pattern)) |
                (Order.receiver_address.ilike(search_pattern)) |
                (Order.item_name.ilike(search_pattern))
            ).all()

            return orders
        except Exception as e:
            print(f"Error searching orders: {e}")
            return []
        finally:
            session.close()

    def filter_orders(self, search_query: str = "", status: str = "", days: int = 0, province: str = ""):
        """
        Filter orders by multiple criteria.
        :param search_query: Search text
        :param status: Status filter (empty = all)
        :param days: Date range in days (0 = all)
        :param province: Province filter (empty = all)
        :return: List of filtered orders
        """
        from datetime import datetime, timedelta
        from sqlalchemy import and_, or_

        session: Session = SessionLocal()
        try:
            query = session.query(Order)
            conditions = []

            # Status filter
            if status and status != "Tất cả trạng thái":
                conditions.append(Order.status == status)

            # Date filter
            if days > 0:
                cutoff_date = datetime.now() - timedelta(days=days)
                conditions.append(Order.created_at >= cutoff_date)

            # Province filter (check both sender and receiver)
            if province and province != "Tất cả tỉnh thành":
                conditions.append(
                    or_(
                        Order.sender_province.ilike(f"%{province}%"),
                        Order.receiver_province.ilike(f"%{province}%")
                    )
                )

            # Search filter
            if search_query and search_query.strip():
                search_pattern = f"%{search_query.strip()}%"
                conditions.append(
                    or_(
                        Order.id.like(search_pattern),
                        Order.sender_name.ilike(search_pattern),
                        Order.receiver_name.ilike(search_pattern),
                        Order.sender_phone.ilike(search_pattern),
                        Order.receiver_phone.ilike(search_pattern)
                    )
                )

            if conditions:
                query = query.filter(and_(*conditions))

            orders = query.all()
            return orders
        except Exception as e:
            print(f"Error filtering orders: {e}")
            return []
        finally:
            session.close()

    def get_unique_provinces(self):
        """Get list of unique provinces from all orders."""
        session: Session = SessionLocal()
        try:
            sender_provinces = session.query(Order.sender_province).distinct().all()
            receiver_provinces = session.query(Order.receiver_province).distinct().all()

            all_provinces = set()
            for (prov,) in sender_provinces + receiver_provinces:
                if prov and prov.strip():
                    all_provinces.add(prov.strip())

            return sorted(list(all_provinces))
        except Exception as e:
            print(f"Error getting provinces: {e}")
            return []
        finally:
            session.close()

    def update_order_status(self, order_id, new_status, changed_by=None, note=None):
        """
        Update the status of a specific order and record history.
        """
        session: Session = SessionLocal()
        try:
            order = session.query(Order).filter(Order.id == order_id).first()
            if order:
                old_status = order.status
                order.status = new_status

                # Record status change history
                from models.order_status_history import OrderStatusHistory
                history = OrderStatusHistory(
                    order_id=order_id,
                    old_status=old_status,
                    new_status=new_status,
                    changed_by=changed_by,
                    note=note
                )
                session.add(history)
                session.commit()
                return True, f"Updated Order #{order.tracking_code} to '{new_status}'"
            else:
                return False, "Order not found"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    def get_status_history(self, order_id):
        """
        Get status change history for an order.
        """
        session: Session = SessionLocal()
        try:
            from models.order_status_history import OrderStatusHistory
            history = session.query(OrderStatusHistory).filter(
                OrderStatusHistory.order_id == order_id
            ).order_by(OrderStatusHistory.changed_at.asc()).all()
            return history
        except Exception as e:
            print(f"Error fetching status history: {e}")
            return []
        finally:
            session.close()

    def delete_order(self, order_id):
        """
        Delete a specific order by ID.
        """
        session: Session = SessionLocal()
        try:
            order = session.query(Order).filter(Order.id == order_id).first()
            if order:
                tracking_code = order.tracking_code
                session.delete(order)
                session.commit()
                return True, f"Deleted Order #{tracking_code} successfully"
            else:
                return False, "Order not found"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    def get_order_by_id(self, order_id):
        """
        Get a specific order by ID.
        """
        session: Session = SessionLocal()
        try:
            order = session.query(Order).filter(Order.id == order_id).first()
            if order:
                # Return order data as dict to avoid session issues
                return {
                    'id': order.id,
                    'tracking_code': order.tracking_code,
                    'order_type': order.order_type or 'domestic',
                    'sender_name': order.sender_name or '',
                    'sender_phone': order.sender_phone or '',
                    'sender_email': order.sender_email or '',
                    'sender_address': order.sender_address or '',
                    'sender_province': order.sender_province or '',
                    'receiver_name': order.receiver_name or '',
                    'receiver_phone': order.receiver_phone or '',
                    'receiver_email': order.receiver_email or '',
                    'receiver_address': order.receiver_address or '',
                    'receiver_province': order.receiver_province or '',
                    'item_name': order.item_name or '',
                    'item_type': order.item_type or 'normal',
                    'package_count': order.package_count or 1,
                    'weight': order.weight or 0.0,
                    'dimensions': order.dimensions or '',
                    'service_type': order.service_type or 'standard',
                    'delivery_note': order.delivery_note or '',
                    'payment_type': order.payment_type or 'sender',
                    'shipping_cost': order.shipping_cost or 0.0,
                    'has_cod': order.has_cod or False,
                    'cod_amount': order.cod_amount or 0.0,
                    'status': order.status,
                    'created_at': order.created_at
                }
            return None
        except Exception as e:
            print(f"Error fetching order: {e}")
            return None
        finally:
            session.close()

    def update_order(self, order_id, data: dict):
        """
        Update an existing order with new data.
        """
        session: Session = SessionLocal()
        try:
            order = session.query(Order).filter(Order.id == order_id).first()
            if order:
                # Update all fields
                order.tracking_code = data.get('tracking_code', order.tracking_code)
                order.order_type = data.get('order_type', order.order_type)
                order.sender_name = data.get('sender_name', order.sender_name)
                order.sender_phone = data.get('sender_phone', order.sender_phone)
                order.sender_email = data.get('sender_email', order.sender_email)
                order.sender_address = data.get('sender_address', order.sender_address)
                order.sender_province = data.get('sender_province', order.sender_province)
                order.sender_ward = data.get('sender_ward', order.sender_ward)
                order.receiver_name = data.get('receiver_name', order.receiver_name)
                order.receiver_phone = data.get('receiver_phone', order.receiver_phone)
                order.receiver_email = data.get('receiver_email', order.receiver_email)
                order.receiver_address = data.get('receiver_address', order.receiver_address)
                order.receiver_province = data.get('receiver_province', order.receiver_province)
                order.receiver_ward = data.get('receiver_ward', order.receiver_ward)
                order.item_name = data.get('item_name', order.item_name)
                order.item_type = data.get('item_type', order.item_type)
                order.package_count = int(data.get('package_count', order.package_count or 1))
                order.weight = float(data.get('weight', order.weight or 0))
                order.dimensions = data.get('dimensions', order.dimensions)
                order.service_type = data.get('service_type', order.service_type)
                order.delivery_note = data.get('delivery_note', order.delivery_note)
                order.payment_type = data.get('payment_type', order.payment_type)
                order.shipping_cost = float(data.get('shipping_cost', order.shipping_cost or 0))
                order.has_cod = data.get('has_cod', order.has_cod)
                order.cod_amount = float(data.get('cod_amount', order.cod_amount or 0))

                session.commit()
                return True, f"Updated Order #{order.tracking_code} successfully"
            else:
                return False, "Order not found"
        except Exception as e:
            session.rollback()
            return False, f"Error updating order: {str(e)}"
        finally:
            session.close()
