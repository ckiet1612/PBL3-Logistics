# ui/route_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QTableWidget, QTableWidgetItem,
                              QHeaderView, QFormLayout, QMessageBox, QMenu)
from PyQt6.QtCore import Qt
from services.route_service import RouteService
from ui.base_dialog import BaseDialog
from ui.constants import (BUTTON_STYLE_GREEN,
                          BUTTON_STYLE_GRAY, TABLE_STYLE,
                          HEADER_STYLE_LARGE, FOOTER_STYLE)



class AddRouteDialog(BaseDialog):
    """Dialog to add/edit route."""
    def __init__(self, parent=None, route_data=None):
        title = "Sửa tuyến" if route_data else "Thêm tuyến mới"
        super().__init__(parent, title=title, min_width=340, min_height=290)
        self.route_data = route_data
        self.setFixedSize(340, 290)
        self.setup_ui()

        if route_data:
            self.load_data()

    def setup_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Origin/Destination Province - using BaseDialog helper
        self.cmb_origin = self.create_province_combo(with_completer=False)
        layout.addRow("Tỉnh xuất phát:", self.cmb_origin)

        self.cmb_dest = self.create_province_combo(with_completer=False)
        layout.addRow("Tỉnh đích:", self.cmb_dest)

        # Distance - using BaseDialog helper
        self.spin_distance = self.create_double_spin_box(0, 5000, 0, 1, " km")
        layout.addRow("Khoảng cách:", self.spin_distance)

        # Estimated hours
        self.spin_hours = self.create_double_spin_box(0, 100, 0, 1, " giờ")
        layout.addRow("Thời gian dự kiến:", self.spin_hours)

        # Base price
        self.spin_base_price = self.create_double_spin_box(0, 10000000, 0, 0, " VND")
        self.spin_base_price.setSingleStep(10000)
        layout.addRow("Giá cước cơ bản:", self.spin_base_price)

        # Price per kg
        self.spin_price_per_kg = self.create_double_spin_box(0, 100000, 5000, 0, " VND/kg")
        self.spin_price_per_kg.setSingleStep(1000)
        layout.addRow("Phí theo cân:", self.spin_price_per_kg)

        # Buttons - using BaseDialog helper
        self.setup_custom_buttons(layout)

    def load_data(self):
        """Load existing route data."""
        if self.route_data:
            # Using BaseDialog set_combo_value
            self.set_combo_value(self.cmb_origin, self.route_data.origin_province)
            self.set_combo_value(self.cmb_dest, self.route_data.dest_province)

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
        title_label.setStyleSheet(HEADER_STYLE_LARGE)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        self.btn_refresh = QPushButton("🔄 Làm mới")
        self.btn_refresh.setStyleSheet(BUTTON_STYLE_GRAY)
        self.btn_refresh.clicked.connect(self.load_routes)
        header_layout.addWidget(self.btn_refresh)

        self.btn_add = QPushButton("➕ Thêm tuyến")
        self.btn_add.setStyleSheet(BUTTON_STYLE_GREEN)
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

        # Use consistent styling from constants
        self.table.setStyleSheet(TABLE_STYLE)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.doubleClicked.connect(self.edit_route)

        layout.addWidget(self.table)

        # Footer
        self.lbl_footer = QLabel("Tổng: 0 tuyến")
        self.lbl_footer.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl_footer.setStyleSheet(FOOTER_STYLE)
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
