# ui/user_management_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QTableWidget, QTableWidgetItem,
                              QHeaderView, QDialog, QLineEdit, QComboBox,
                              QFormLayout, QMessageBox, QMenu)
from PyQt6.QtCore import Qt
from ui.constants import (BUTTON_STYLE_GREEN, BUTTON_STYLE_GRAY, TABLE_STYLE)

class AddUserDialog(QDialog):
    """Dialog to add a new user."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Thêm tài khoản mới")
        self.setFixedSize(350, 250)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Username
        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("Nhập tên đăng nhập")
        layout.addRow("Tên đăng nhập:", self.txt_username)

        # Password
        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("Nhập mật khẩu")
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Mật khẩu:", self.txt_password)

        # Full Name
        self.txt_fullname = QLineEdit()
        self.txt_fullname.setPlaceholderText("Nhập tên đầy đủ")
        layout.addRow("Họ và tên:", self.txt_fullname)

        # Role
        self.cmb_role = QComboBox()
        self.cmb_role.addItems(["staff", "admin"])
        layout.addRow("Vai trò:", self.cmb_role)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Lưu")
        self.btn_save.clicked.connect(self.accept)
        self.btn_cancel = QPushButton("Huỷ")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_cancel)
        layout.addRow(btn_layout)

    def get_data(self):
        return {
            'username': self.txt_username.text().strip(),
            'password': self.txt_password.text(),
            'full_name': self.txt_fullname.text().strip(),
            'role': self.cmb_role.currentText()
        }


class UserManagementTab(QWidget):
    """Tab for managing users (Admin only)."""
    def __init__(self, auth_service, current_user):
        super().__init__()
        self.auth_service = auth_service
        self.current_user = current_user
        self.setup_ui()
        self.load_users()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("👥 Quản lý tài khoản")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        self.btn_refresh = QPushButton("🔄 Làm mới")
        self.btn_refresh.setStyleSheet(BUTTON_STYLE_GRAY)
        self.btn_refresh.clicked.connect(self.load_users)
        header_layout.addWidget(self.btn_refresh)

        self.btn_add = QPushButton("➕ Thêm tài khoản")
        self.btn_add.setStyleSheet(BUTTON_STYLE_GREEN)
        self.btn_add.clicked.connect(self.add_user)
        header_layout.addWidget(self.btn_add)

        layout.addLayout(header_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Username", "Họ tên", "Vai trò", "Ngày tạo"])

        # Consistent layout with other tabs
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(5)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Username
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Họ tên
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Vai trò
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Ngày tạo

        # Set minimum widths
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 200)

        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(40)

        # Use simple consistent styling from MainWindow
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #ddd;
                border: 1px solid #ccc;
                background-color: white;
                alternate-background-color: #f9f9f9;
            }
            QTableWidget::item {
                padding-left: 5px;
            }
            QHeaderView::section {
                background-color: #e8e8e8;
                padding: 10px 8px;
                border: none;
                border-bottom: 2px solid #666;
                border-right: 1px solid #ccc;
                font-weight: bold;
                font-size: 13px;
            }
        """)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.table)

    def load_users(self):
        """Load all users into the table."""
        users = self.auth_service.get_all_users()

        self.table.setRowCount(0)
        for row_idx, user in enumerate(users):
            self.table.insertRow(row_idx)

            id_item = QTableWidgetItem(str(user.id))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 0, id_item)

            username_item = QTableWidgetItem(user.username)
            username_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 1, username_item)

            fullname_item = QTableWidgetItem(user.full_name or "")
            fullname_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 2, fullname_item)

            role_item = QTableWidgetItem(user.role.upper())
            role_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if user.role == 'admin':
                role_item.setForeground(Qt.GlobalColor.darkGreen)
            self.table.setItem(row_idx, 3, role_item)

            created = user.created_at.strftime("%d/%m/%Y %H:%M") if user.created_at else ""
            created_item = QTableWidgetItem(created)
            created_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 4, created_item)

    def add_user(self):
        """Open dialog to add new user."""
        dialog = AddUserDialog(self)
        if dialog.exec():
            data = dialog.get_data()

            if not data['username'] or not data['password']:
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ username và password")
                return

            success, message = self.auth_service.create_user(data)
            if success:
                QMessageBox.information(self, "Thành công", message)
                self.load_users()
            else:
                QMessageBox.critical(self, "Lỗi", message)

    def show_context_menu(self, pos):
        """Show delete option on right-click."""
        from PyQt6.QtWidgets import QMenu

        index = self.table.indexAt(pos)
        if not index.isValid():
            return

        row = index.row()
        user_id = int(self.table.item(row, 0).text())
        username = self.table.item(row, 1).text()

        # Don't allow deleting own account
        if user_id == self.current_user['id']:
            return

        menu = QMenu()
        action_delete = menu.addAction("🗑️ Xoá tài khoản")

        action = menu.exec(self.table.viewport().mapToGlobal(pos))

        if action == action_delete:
            self.delete_user(user_id, username)

    def delete_user(self, user_id, username):
        """Delete a user after confirmation."""
        reply = QMessageBox.question(
            self,
            "Xác nhận xoá",
            f"Bạn có chắc chắn muốn xoá tài khoản '{username}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.auth_service.delete_user(user_id)
            if success:
                self.load_users()
                QMessageBox.information(self, "Thành công", message)
            else:
                QMessageBox.warning(self, "Lỗi", message)
