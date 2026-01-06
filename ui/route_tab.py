# ui/route_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QTableWidget, QTableWidgetItem,
                              QHeaderView, QDialog, QComboBox,
                              QFormLayout, QMessageBox, QDoubleSpinBox,
                              QMenu)
from PyQt6.QtCore import Qt
from services.route_service import RouteService

# Vietnam provinces for dropdown
VIETNAM_PROVINCES = [
    "", "Hà Nội", "TP. Hồ Chí Minh", "Hải Phòng", "Đà Nẵng", "Cần Thơ", "Huế",
    "Cao Bằng", "Điện Biên", "Lai Châu", "Sơn La", "Lạng Sơn", "Quảng Ninh",
    "Thanh Hóa", "Nghệ An", "Hà Tĩnh", "Tuyên Quang", "Lào Cai", "Thái Nguyên",
    "Phú Thọ", "Bắc Ninh", "Hưng Yên", "Ninh Bình", "Quảng Trị", "Quảng Ngãi",
    "Gia Lai", "Khánh Hòa", "Lâm Đồng", "Đắk Lắk", "Đồng Nai", "Tây Ninh",
    "Vĩnh Long", "Đồng Tháp", "Cà Mau", "An Giang"
]


class AddRouteDialog(QDialog):
    """Dialog to add/edit route."""
    def __init__(self, parent=None, route_data=None):
        super().__init__(parent)
        self.route_data = route_data
        self.setWindowTitle("Sửa tuyến" if route_data else "Thêm tuyến mới")
        self.setFixedSize(420, 380)
        self.setup_ui()
        
        if route_data:
            self.load_data()
    
    def setup_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Origin Province
        self.cmb_origin = QComboBox()
        self.cmb_origin.addItems(VIETNAM_PROVINCES)
        layout.addRow("Tỉnh xuất phát:", self.cmb_origin)
        
        # Destination Province
        self.cmb_dest = QComboBox()
        self.cmb_dest.addItems(VIETNAM_PROVINCES)
        layout.addRow("Tỉnh đích:", self.cmb_dest)
        
        # Distance
        self.spin_distance = QDoubleSpinBox()
        self.spin_distance.setRange(0, 5000)
        self.spin_distance.setDecimals(1)
        self.spin_distance.setSuffix(" km")
        layout.addRow("Khoảng cách:", self.spin_distance)
        
        # Estimated hours
        self.spin_hours = QDoubleSpinBox()
        self.spin_hours.setRange(0, 100)
        self.spin_hours.setDecimals(1)
        self.spin_hours.setSuffix(" giờ")
        layout.addRow("Thời gian dự kiến:", self.spin_hours)
        
        # Base price
        self.spin_base_price = QDoubleSpinBox()
        self.spin_base_price.setRange(0, 10000000)
        self.spin_base_price.setDecimals(0)
        self.spin_base_price.setSingleStep(10000)
        self.spin_base_price.setSuffix(" VND")
        layout.addRow("Giá cước cơ bản:", self.spin_base_price)
        
        # Price per kg
        self.spin_price_per_kg = QDoubleSpinBox()
        self.spin_price_per_kg.setRange(0, 100000)
        self.spin_price_per_kg.setDecimals(0)
        self.spin_price_per_kg.setSingleStep(1000)
        self.spin_price_per_kg.setValue(5000)
        self.spin_price_per_kg.setSuffix(" VND/kg")
        layout.addRow("Phí theo cân:", self.spin_price_per_kg)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Lưu")
        self.btn_save.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px 20px;")
        self.btn_save.clicked.connect(self.accept)
        
        self.btn_cancel = QPushButton("Huỷ")
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_cancel)
        layout.addRow(btn_layout)
    
    def load_data(self):
        """Load existing route data."""
        if self.route_data:
            idx = self.cmb_origin.findText(self.route_data.origin_province or "")
            if idx >= 0:
                self.cmb_origin.setCurrentIndex(idx)
            
            idx = self.cmb_dest.findText(self.route_data.dest_province or "")
            if idx >= 0:
                self.cmb_dest.setCurrentIndex(idx)
            
            self.spin_distance.setValue(self.route_data.distance_km or 0)
            self.spin_hours.setValue(self.route_data.est_hours or 0)
            self.spin_base_price.setValue(self.route_data.base_price or 0)
            self.spin_price_per_kg.setValue(self.route_data.price_per_kg or 5000)
    
    def get_data(self):
        return {
            'origin_province': self.cmb_origin.currentText(),
            'dest_province': self.cmb_dest.currentText(),
            'distance_km': self.spin_distance.value(),
            'est_hours': self.spin_hours.value(),
            'base_price': self.spin_base_price.value(),
            'price_per_kg': self.spin_price_per_kg.value()
        }


class RouteTab(QWidget):
    """Tab for route management."""
    def __init__(self):
        super().__init__()
        self.service = RouteService()
        self.setup_ui()
        self.load_routes()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("🛣️ Quản lý Tuyến đường")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self.btn_refresh = QPushButton("🔄 Làm mới")
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #607D8B;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #546E7A; }
        """)
        self.btn_refresh.clicked.connect(self.load_routes)
        header_layout.addWidget(self.btn_refresh)
        
        self.btn_add = QPushButton("➕ Thêm tuyến")
        self.btn_add.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        self.btn_add.clicked.connect(self.add_route)
        header_layout.addWidget(self.btn_add)
        
        layout.addLayout(header_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Xuất phát", "Đích", "Khoảng cách", "Thời gian", "Giá cơ bản", "Số đơn"
        ])
        
        # Consistent layout with other tabs
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(5)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Xuất phát stretch
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Đích stretch
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        
        # Set minimum widths
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 150)
        
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
        self.table.doubleClicked.connect(self.edit_route)
        
        layout.addWidget(self.table)
        
        # Footer
        self.lbl_footer = QLabel("Tổng: 0 tuyến")
        self.lbl_footer.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl_footer.setStyleSheet("font-size: 13px; color: #555; padding: 5px 10px;")
        layout.addWidget(self.lbl_footer)
    
    def load_routes(self):
        """Load all routes with stats into table."""
        stats = self.service.get_route_stats()
        
        self.table.setRowCount(0)
        for row_idx, stat in enumerate(stats):
            route = stat['route']
            order_count = stat['order_count']
            
            self.table.insertRow(row_idx)
            
            # ID
            id_item = QTableWidgetItem(str(route.id))
            id_item.setData(Qt.ItemDataRole.UserRole, route.id)
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 0, id_item)
            
            # Origin
            origin_item = QTableWidgetItem(route.origin_province)
            origin_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 1, origin_item)
            
            # Destination
            dest_item = QTableWidgetItem(route.dest_province)
            dest_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 2, dest_item)
            
            # Distance
            dist_item = QTableWidgetItem(f"{route.distance_km:.0f} km")
            dist_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 3, dist_item)
            
            # Est hours
            time_item = QTableWidgetItem(f"{route.est_hours:.1f} giờ")
            time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 4, time_item)
            
            # Base price
            price_item = QTableWidgetItem(f"{route.base_price:,.0f} VND")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 5, price_item)
            
            # Order count
            count_item = QTableWidgetItem(str(order_count))
            count_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 6, count_item)
        
        self.lbl_footer.setText(f"Tổng: {len(stats)} tuyến")
    
    def add_route(self):
        """Add new route."""
        dialog = AddRouteDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if not data['origin_province'] or not data['dest_province']:
                QMessageBox.warning(self, "Lỗi", "Vui lòng chọn tỉnh xuất phát và tỉnh đích")
                return
            
            if data['origin_province'] == data['dest_province']:
                QMessageBox.warning(self, "Lỗi", "Tỉnh xuất phát và tỉnh đích không được trùng nhau")
                return
            
            success, msg = self.service.create_route(data)
            if success:
                QMessageBox.information(self, "Thành công", msg)
                self.load_routes()
            else:
                QMessageBox.critical(self, "Lỗi", msg)
    
    def edit_route(self):
        """Edit selected route."""
        row = self.table.currentRow()
        if row < 0:
            return
        
        route_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        route = self.service.get_route_by_id(route_id)
        
        if route:
            dialog = AddRouteDialog(self, route)
            if dialog.exec():
                data = dialog.get_data()
                success, msg = self.service.update_route(route_id, data)
                if success:
                    self.load_routes()
                else:
                    QMessageBox.critical(self, "Lỗi", msg)
    
    def show_context_menu(self, pos):
        """Show right-click menu."""
        index = self.table.indexAt(pos)
        if not index.isValid():
            return
        
        row = index.row()
        route_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        menu = QMenu()
        action_edit = menu.addAction("✏️ Sửa tuyến")
        action_delete = menu.addAction("🗑️ Xóa tuyến")
        
        action = menu.exec(self.table.viewport().mapToGlobal(pos))
        
        if action == action_edit:
            self.edit_route()
        elif action == action_delete:
            self.delete_route(route_id)
    
    def delete_route(self, route_id):
        """Delete route after confirmation."""
        reply = QMessageBox.question(
            self, "Xác nhận xóa",
            "Bạn có chắc chắn muốn xóa tuyến đường này?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, msg = self.service.delete_route(route_id)
            if success:
                self.load_routes()
            else:
                QMessageBox.warning(self, "Lỗi", msg)
