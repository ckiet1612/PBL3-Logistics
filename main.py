# main.py
import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox

def init_database():
    """Initialize database if it doesn't exist."""
    from database.db_connection import engine, DB_PATH
    from models.base import Base
    from models.order import Order
    from models.user import User
    from models.warehouse import Warehouse, OrderWarehouseHistory
    from models.route import Route
    from models.order_status_history import OrderStatusHistory

    # Create database tables if they don't exist
    if not os.path.exists(DB_PATH):
        print("First run - Creating database...")

    Base.metadata.create_all(bind=engine)

def main():
    app = QApplication(sys.argv)

    # Auto-initialize database on first run
    init_database()

    from services.auth_service import AuthService
    from ui.login_dialog import LoginDialog
    from controllers.main_controller import MainController

    # Initialize Auth Service
    auth_service = AuthService()

    # Create default admin if needed (for first run)
    auth_service.create_default_admin()

    # Show Login Dialog
    login_dialog = LoginDialog(auth_service)

    if login_dialog.exec():
        # Login successful - get user data
        user_data = login_dialog.get_user_data()

        # Initialize the Controller with user data
        controller = MainController(user_data=user_data, auth_service=auth_service)

        # Connect logout signal
        def handle_logout():
            controller.view.close()
            # Restart login
            main()

        controller.view.logout_requested.connect(handle_logout)

        sys.exit(app.exec())
    else:
        # Login cancelled
        sys.exit(0)

if __name__ == "__main__":
    main()
