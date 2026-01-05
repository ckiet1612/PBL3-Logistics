# ui/main_window.py
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QTableWidget, QHBoxLayout, 
                             QHeaderView, QLabel, QLineEdit, QComboBox,
                             QListWidget, QListWidgetItem, QStackedWidget, QSplitter)
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from ui.dashboard_tab import DashboardTab

class MainWindow(QMainWindow):
    logout_requested = pyqtSignal()  # Signal for logout
    
    def __init__(self, user_data=None, auth_service=None):
        super().__init__()
        self.user_data = user_data or {}
        self.auth_service = auth_service
        self.is_admin = self.user_data.get('is_admin', False)
        
        self.setWindowTitle("Logistics Management System - PBL3")
        self.setGeometry(100, 100, 1300, 800)

        # Main Container
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Initialize Status Bar for notifications
        self.statusBar().showMessage("Sẵn sàng", 2000)

        # Initialize UI
        self.setup_user_bar()
        self.setup_ui()

    def setup_user_bar(self):
        """Setup the user info and logout bar."""
        user_bar = QHBoxLayout()
        
        # User info
        role_text = "👑 Admin" if self.is_admin else "👤 Staff"
        user_label = QLabel(f"{role_text}: {self.user_data.get('full_name', self.user_data.get('username', 'User'))}")
        user_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")
        user_bar.addWidget(user_label)
        
        user_bar.addStretch()
        
        # Logout button
        self.btn_logout = QPushButton("🚪 Đăng xuất")
        self.btn_logout.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.btn_logout.clicked.connect(self.logout_requested.emit)
        user_bar.addWidget(self.btn_logout)
        
        self.main_layout.addLayout(user_bar)

    def setup_ui(self):
        # Main horizontal layout with sidebar
        main_container = QHBoxLayout()
        main_container.setContentsMargins(0, 0, 0, 0)
        main_container.setSpacing(5)
        
        # --- LEFT SIDEBAR ---
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(180)
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 8px;
                font-size: 14px;
                padding: 3px;
            }
            QListWidget::item {
                color: #333;
                padding: 10px 8px;
                margin: 1px 0;
                border-radius: 6px;
            }
            QListWidget::item:selected {
                background-color: #4CAF50;
                color: white;
            }
            QListWidget::item:hover:!selected {
                background-color: #2196F3;
                color: white;
            }
        """)
        
        # Add sidebar items
        self.sidebar.addItem(QListWidgetItem("📦 Quản lý Đơn"))
        self.sidebar.addItem(QListWidgetItem("📊 Dashboard"))
        self.sidebar.addItem(QListWidgetItem("🏭 Kho bãi"))
        self.sidebar.addItem(QListWidgetItem("🛣️ Tuyến đường"))
        if self.is_admin and self.auth_service:
            self.sidebar.addItem(QListWidgetItem("👥 Người dùng"))
        
        self.sidebar.setCurrentRow(0)
        self.sidebar.currentRowChanged.connect(self.on_sidebar_changed)
        
        main_container.addWidget(self.sidebar)
        
        # --- RIGHT CONTENT (Stacked Pages) ---
        self.pages = QStackedWidget()
        
        # Page 1: Orders
        self.tab_orders = QWidget()
        self.setup_orders_tab()
        self.pages.addWidget(self.tab_orders)
        
        # Page 2: Dashboard
        self.tab_dashboard = DashboardTab()
        self.pages.addWidget(self.tab_dashboard)
        
        # Page 3: Warehouse
        from ui.warehouse_tab import WarehouseTab
        self.tab_warehouse = WarehouseTab()
        self.pages.addWidget(self.tab_warehouse)
        
        # Page 4: Routes
        from ui.route_tab import RouteTab
        self.tab_routes = RouteTab()
        self.pages.addWidget(self.tab_routes)
        
        # Page 5: User Management (Admin only)
        if self.is_admin and self.auth_service:
            from ui.user_management_tab import UserManagementTab
            self.tab_users = UserManagementTab(self.auth_service, self.user_data)
            self.pages.addWidget(self.tab_users)
        
        main_container.addWidget(self.pages)
        self.main_layout.addLayout(main_container)
    
    def on_sidebar_changed(self, index):
        """Switch page when sidebar item is selected."""
        self.pages.setCurrentIndex(index)

    def setup_orders_tab(self):
        """Setup the layout for the Order List tab."""
        layout = QVBoxLayout(self.tab_orders)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(5)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("📦 Quản lý Đơn hàng")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Tìm kiếm theo mã, tên, SĐT...")
        self.search_input.setMinimumWidth(250)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 5px 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
        """)
        header_layout.addWidget(self.search_input)
        
        self.btn_refresh = QPushButton("🔄 Làm mới")
        header_layout.addWidget(self.btn_refresh)
        
        # Filter toggle button
        self.btn_toggle_filter = QPushButton("⚙️ Bộ lọc")
        self.btn_toggle_filter.setCheckable(True)
        self.btn_toggle_filter.setChecked(False)
        self.btn_toggle_filter.setStyleSheet("""
            QPushButton {
                background-color: #607D8B;
                color: white;
                padding: 5px 12px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #546E7A; }
            QPushButton:checked { background-color: #455A64; }
        """)
        self.btn_toggle_filter.clicked.connect(self.toggle_filter_panel)
        header_layout.addWidget(self.btn_toggle_filter)
        
        layout.addLayout(header_layout)

        # Filter Panel (collapsible)
        self.filter_panel = QWidget()
        filter_layout = QHBoxLayout(self.filter_panel)
        filter_layout.setContentsMargins(0, 5, 0, 5)
        
        filter_label = QLabel("🎛️ Lọc:")
        filter_layout.addWidget(filter_label)
        
        # Status filter
        self.filter_status = QComboBox()
        self.filter_status.addItems(["Tất cả trạng thái", "Đang xử lý", "Đang giao", "Đã giao", "Đã hủy"])
        self.filter_status.setMinimumWidth(130)
        filter_layout.addWidget(self.filter_status)
        
        # Time filter
        self.filter_time = QComboBox()
        self.filter_time.addItems(["Tất cả thời gian", "Hôm nay", "7 ngày qua", "30 ngày qua"])
        self.filter_time.setMinimumWidth(130)
        filter_layout.addWidget(self.filter_time)
        
        # Province filter (sender)
        self.filter_province = QComboBox()
        self.filter_province.addItem("Tất cả tỉnh thành")
        self.filter_province.setMinimumWidth(150)
        filter_layout.addWidget(self.filter_province)
        
        # Clear filter button
        self.btn_clear_filter = QPushButton("🗑️ Xoá lọc")
        self.btn_clear_filter.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 5px 12px;
                border-radius: 3px;
            }
            QPushButton:hover { background-color: #d32f2f; }
        """)
        filter_layout.addWidget(self.btn_clear_filter)
        
        filter_layout.addStretch()
        
        # Hidden by default
        self.filter_panel.setVisible(False)
        layout.addWidget(self.filter_panel)

        # Table with new columns
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Mã đơn", "Trạng thái", "Người gửi → Người nhận", 
            "Tuyến đường", "Số kiện / KL", "Tổng phí", "Thời gian tạo"
        ])
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Mã đơn
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Trạng thái
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Người gửi → Người nhận
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Tuyến đường
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Số kiện / KL
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Tổng phí
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Thời gian tạo
        
        # Set minimum widths for stretch columns
        self.table.setColumnWidth(2, 350)  # Người gửi → Người nhận (Wider)
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)
        self.table.setSortingEnabled(True)  # Enable sorting by clicking headers
        
        # Set row height
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #ccc;
                border: 1px solid #bbb;
                background-color: white;
                alternate-background-color: #f9f9f9;
            }
            QTableWidget::item {
                padding: 6px;
                border-bottom: 1px solid #ddd;
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
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 4px 10px;
                border-radius: 4px;
                font-size: 12px;
                min-width: 70px;
                min-height: 26px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        layout.addWidget(self.table)

        # Quick Stats Footer
        self.lbl_quick_stats = QLabel("📦 Tổng: 0 | 🆕 Mới: 0 | 🚚 Đang giao: 0 | ✅ Đã giao: 0")
        self.lbl_quick_stats.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl_quick_stats.setStyleSheet("font-size: 13px; color: #555; padding: 5px 10px;")
        layout.addWidget(self.lbl_quick_stats)

        # Action Buttons
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("➕ Thêm đơn hàng")
        self.btn_scan_ai = QPushButton("📷 Scan với OCR.space")
        self.btn_export = QPushButton("📊 Xuất Excel")
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_scan_ai)
        btn_layout.addWidget(self.btn_export)
        layout.addLayout(btn_layout)
    
    def toggle_filter_panel(self):
        """Toggle visibility of filter panel."""
        is_visible = self.btn_toggle_filter.isChecked()
        self.filter_panel.setVisible(is_visible)
        
        # Update button text
        if is_visible:
            self.btn_toggle_filter.setText("⚙️ Ẩn lọc")
        else:
            self.btn_toggle_filter.setText("⚙️ Bộ lọc")