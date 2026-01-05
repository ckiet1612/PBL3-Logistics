# main.py
import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from services.auth_service import AuthService
from ui.login_dialog import LoginDialog
from controllers.main_controller import MainController

def main():
    app = QApplication(sys.argv)
    
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