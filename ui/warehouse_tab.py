# ui/warehouse_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QTableWidget, QTableWidgetItem,
                              QHeaderView, QDialog, QLineEdit, QComboBox,
                              QFormLayout, QMessageBox, QSpinBox, QTextEdit,
                              QMenu, QProgressBar)
from PyQt6.QtCore import Qt
from services.warehouse_service import WarehouseService
from ui.constants import (VIETNAM_PROVINCES, BUTTON_STYLE_GREEN,
                          BUTTON_STYLE_GRAY, TABLE_STYLE)



class AddWarehouseDialog(QDialog):
    """Dialog to add/edit warehouse."""
    def __init__(self, parent=None, warehouse_data=None):
        super().__init__(parent)
        self.warehouse_data = warehouse_data
        self.setWindowTitle("Sửa kho" if warehouse_data else "Thêm kho mới")
        self.setFixedSize(400, 350)
        self.setup_ui()

        if warehouse_data:
            self.load_data()

    def setup_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Name
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Nhập tên kho")
        layout.addRow("Tên kho:", self.txt_name)

        # Address
        self.txt_address = QTextEdit()
        self.txt_address.setMaximumHeight(60)
        self.txt_address.setPlaceholderText("Địa chỉ chi tiết")
        layout.addRow("Địa chỉ:", self.txt_address)

        # Province
        self.cmb_province = QComboBox()
        self.cmb_province.addItems(VIETNAM_PROVINCES)
        layout.addRow("Tỉnh/Thành:", self.cmb_province)

        # Capacity
        self.spin_capacity = QSpinBox()
        self.spin_capacity.setRange(1, 10000)
        self.spin_capacity.setValue(100)
        layout.addRow("Sức chứa (đơn):", self.spin_capacity)

        # Status
        self.cmb_status = QComboBox()
        self.cmb_status.addItems(["Hoạt động", "Bảo trì", "Đóng cửa"])
        layout.addRow("Trạng thái:", self.cmb_status)

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
        """Load existing warehouse data."""
        if self.warehouse_data:
            self.txt_name.setText(self.warehouse_data.name or "")
            self.txt_address.setPlainText(self.warehouse_data.address or "")

            idx = self.cmb_province.findText(self.warehouse_data.province or "")
            if idx >= 0:
                self.cmb_province.setCurrentIndex(idx)

            self.spin_capacity.setValue(self.warehouse_data.capacity or 100)

            status_map = {'active': 0, 'maintenance': 1, 'closed': 2}
            self.cmb_status.setCurrentIndex(status_map.get(self.warehouse_data.status, 0))

    def get_data(self):
        status_map = {0: 'active', 1: 'maintenance', 2: 'closed'}
        return {
            'name': self.txt_name.text().strip(),
            'address': self.txt_address.toPlainText().strip(),
            'province': self.cmb_province.currentText(),
            'capacity': self.spin_capacity.value(),
            'status': status_map.get(self.cmb_status.currentIndex(), 'active')
        }


class WarehouseTab(QWidget):
    """Tab for warehouse management."""
    def __init__(self):
        super().__init__()
        self.service = WarehouseService()
        self.setup_ui()
        self.load_warehouses()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("🏭 Quản lý Kho bãi")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        self.btn_refresh = QPushButton("🔄 Làm mới")
        self.btn_refresh.setStyleSheet(BUTTON_STYLE_GRAY)
        self.btn_refresh.clicked.connect(self.load_warehouses)
        header_layout.addWidget(self.btn_refresh)

        self.btn_add = QPushButton("➕ Thêm kho")
        self.btn_add.setStyleSheet(BUTTON_STYLE_GREEN)
        self.btn_add.clicked.connect(self.add_warehouse)
        header_layout.addWidget(self.btn_add)

        layout.addLayout(header_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Tên kho", "Tỉnh/Thành", "Sức chứa", "Đang lưu", "Trạng thái"
        ])

        # Consistent layout with other tabs
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(5)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Tên kho stretch
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        # Set minimum widths
        self.table.setColumnWidth(1, 250)
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
        self.table.doubleClicked.connect(self.view_warehouse_orders)

        layout.addWidget(self.table)

        # Footer
        self.lbl_footer = QLabel("Tổng: 0 kho")
        self.lbl_footer.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl_footer.setStyleSheet("font-size: 13px; color: #555; padding: 5px 10px;")
        layout.addWidget(self.lbl_footer)

    def load_warehouses(self):
        """Load all warehouses into table."""
        warehouses = self.service.get_all_warehouses()

        self.table.setRowCount(0)
        for row_idx, wh in enumerate(warehouses):
            self.table.insertRow(row_idx)

            # ID
            id_item = QTableWidgetItem(str(wh.id))
            id_item.setData(Qt.ItemDataRole.UserRole, wh.id)
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 0, id_item)

            # Name
            name_item = QTableWidgetItem(wh.name)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 1, name_item)

            # Province
            province_item = QTableWidgetItem(wh.province or "")
            province_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 2, province_item)

            # Capacity
            capacity_item = QTableWidgetItem(str(wh.capacity))
            capacity_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 3, capacity_item)

            # Current orders
            stats = self.service.get_warehouse_stats(wh.id)
            order_count = stats['order_count'] if stats else 0
            order_item = QTableWidgetItem(str(order_count))
            order_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 4, order_item)

            # Status
            status_item = QTableWidgetItem(wh.get_status_display())
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if wh.status == 'active':
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            elif wh.status == 'maintenance':
                status_item.setForeground(Qt.GlobalColor.darkYellow)
            else:
                status_item.setForeground(Qt.GlobalColor.red)
            self.table.setItem(row_idx, 5, status_item)

        self.lbl_footer.setText(f"Tổng: {len(warehouses)} kho")

    def add_warehouse(self):
        """Add new warehouse."""
        dialog = AddWarehouseDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if not data['name']:
                QMessageBox.warning(self, "Lỗi", "Tên kho không được để trống")
                return

            success, msg = self.service.create_warehouse(data)
            if success:
                QMessageBox.information(self, "Thành công", msg)
                self.load_warehouses()
            else:
                QMessageBox.critical(self, "Lỗi", msg)

    def edit_warehouse(self):
        """Edit selected warehouse (via context menu)."""
        row = self.table.currentRow()
        if row < 0:
            return

        warehouse_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        warehouse = self.service.get_warehouse_by_id(warehouse_id)

        if warehouse:
            dialog = AddWarehouseDialog(self, warehouse)
            if dialog.exec():
                data = dialog.get_data()
                success, msg = self.service.update_warehouse(warehouse_id, data)
                if success:
                    self.load_warehouses()
                else:
                    QMessageBox.critical(self, "Lỗi", msg)

    def view_warehouse_orders(self):
        """View orders in selected warehouse (double-click)."""
        row = self.table.currentRow()
        if row < 0:
            return

        warehouse_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        warehouse_name = self.table.item(row, 1).text()

        from ui.warehouse_orders_dialog import WarehouseOrdersDialog
        dialog = WarehouseOrdersDialog(self, warehouse_id, warehouse_name)
        dialog.exec()

    def show_context_menu(self, pos):
        """Show right-click menu."""
        index = self.table.indexAt(pos)
        if not index.isValid():
            return

        row = index.row()
        warehouse_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        warehouse_name = self.table.item(row, 1).text()

        menu = QMenu()
        action_edit = menu.addAction("✏️ Sửa kho")
        action_delete = menu.addAction("🗑️ Xóa kho")

        action = menu.exec(self.table.viewport().mapToGlobal(pos))

        if action == action_edit:
            self.edit_warehouse()
        elif action == action_delete:
            self.delete_warehouse(warehouse_id, warehouse_name)

    def delete_warehouse(self, warehouse_id, warehouse_name):
        """Delete warehouse after confirmation."""
        reply = QMessageBox.question(
            self, "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa kho '{warehouse_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            success, msg = self.service.delete_warehouse(warehouse_id)
            if success:
                self.load_warehouses()
            else:
                QMessageBox.warning(self, "Lỗi", msg)
