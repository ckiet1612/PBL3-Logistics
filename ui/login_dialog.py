# ui/login_dialog.py
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ui.base_dialog import BaseDialog
from ui.constants import BUTTON_STYLE_PRIMARY, ERROR_STYLE

class LoginDialog(BaseDialog):
    def __init__(self, auth_service, parent=None):
        super().__init__(parent, title="Đăng nhập - Logistics System", min_width=400, min_height=250)
        self.auth_service = auth_service
        self.user_data = None
        self.setFixedSize(400, 250)
        self.setModal(True)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(40, 30, 40, 30)

        # Title
        title = QLabel("🔐 Đăng nhập hệ thống")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Username
        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("Tên đăng nhập")
        self.txt_username.setMinimumHeight(35)
        layout.addWidget(self.txt_username)

        # Password
        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("Mật khẩu")
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.setMinimumHeight(35)
        self.txt_password.returnPressed.connect(self.handle_login)
        layout.addWidget(self.txt_password)

        # Login Button
        self.btn_login = QPushButton("Đăng nhập")
        self.btn_login.setMinimumHeight(40)
        self.btn_login.setStyleSheet(BUTTON_STYLE_PRIMARY)
        self.btn_login.clicked.connect(self.handle_login)
        layout.addWidget(self.btn_login)

        # Error label
        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet(ERROR_STYLE)
        self.lbl_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_error)

    def handle_login(self):
        username = self.txt_username.text().strip()
        password = self.txt_password.text()

        if not username or not password:
            self.lbl_error.setText("Vui lòng nhập đầy đủ thông tin")
            return

        success, result = self.auth_service.authenticate(username, password)

        if success:
            self.user_data = result
            self.accept()
        else:
            self.lbl_error.setText(result)
            self.txt_password.clear()
            self.txt_password.setFocus()

    def get_user_data(self):
        return self.user_data
