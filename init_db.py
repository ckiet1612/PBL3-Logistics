# init_db.py
from database.db_connection import engine
from models.base import Base
# You need to import the child models so that SQLAlchemy knows which table to create
from models.order import Order
from models.user import User
from models.warehouse import Warehouse, OrderWarehouseHistory
from models.route import Route
from models.order_status_history import OrderStatusHistory

print("Initializing the database...")
try:
    # This command will find all classes that inherit from Base and create the corresponding table
    Base.metadata.create_all(bind=engine)
    print("Success! Database tables have been created.")

    # Create default admin account
    from services.auth_service import AuthService
    auth_service = AuthService()
    if auth_service.create_default_admin():
        print("Default admin account created: admin / admin123")
    else:
        print("Admin account already exists.")

except Exception as e:
    print(f"An error occurred: {e}")
