# ui/warehouse_select_dialog.py
from PyQt6.QtWidgets import (QVBoxLayout, QLabel, QListWidget, QListWidgetItem,
                              QLineEdit, QDialogButtonBox)
from PyQt6.QtCore import Qt
from services.warehouse_service import WarehouseService
from ui.base_dialog import BaseDialog
from ui.constants import LIST_STYLE, HEADER_STYLE_SMALL


class WarehouseSelectDialog(BaseDialog):
    """Dialog to search and select a warehouse."""

    def __init__(self, parent=None, order_count=1):
        super().__init__(parent, title="Chọn kho đích", min_width=400, min_height=450)
        self.setFixedSize(400, 450)
        self.service = WarehouseService()
        self.selected_warehouse_id = None
        self.order_count = order_count
        self.setup_ui()
        self.load_warehouses()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel(f"🏭 Chuyển {self.order_count} đơn hàng vào kho")
        header.setStyleSheet(HEADER_STYLE_SMALL)
        layout.addWidget(header)

        # Search box
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("🔍 Tìm kiếm kho...")
        self.txt_search.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 14px;
            }
        """)
        self.txt_search.textChanged.connect(self.filter_warehouses)
        layout.addWidget(self.txt_search)

        # Warehouse list
        self.list_warehouses = QListWidget()
        self.list_warehouses.setStyleSheet(LIST_STYLE)
        self.list_warehouses.itemDoubleClicked.connect(self.accept)
        layout.addWidget(self.list_warehouses)

        # Buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Chuyển kho")
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Huỷ")
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def load_warehouses(self):
        """Load all active warehouses into list."""
        self.all_warehouses = []
        warehouses = self.service.get_all_warehouses()

        for wh in warehouses:
            if wh.status == 'active':
                self.all_warehouses.append(wh)
                self.add_warehouse_item(wh)

    def add_warehouse_item(self, wh):
        """Add warehouse item to list."""
        stats = self.service.get_warehouse_stats(wh.id)
        order_count = stats['order_count'] if stats else 0
        capacity_pct = stats['capacity_pct'] if stats else 0

        text = f"{wh.name}\n📍 {wh.province or 'N/A'} | 📦 {order_count}/{wh.capacity} ({capacity_pct:.0f}%)"

        item = QListWidgetItem(text)
        item.setData(Qt.ItemDataRole.UserRole, wh.id)
        self.list_warehouses.addItem(item)

    def filter_warehouses(self, search_text):
        """Filter warehouses by search text."""
        self.list_warehouses.clear()
        search_lower = search_text.lower().strip()

        for wh in self.all_warehouses:
            if (search_lower in wh.name.lower() or
                search_lower in (wh.province or '').lower() or
                search_lower in (wh.address or '').lower()):
                self.add_warehouse_item(wh)

    def accept(self):
        """Get selected warehouse and close."""
        current_item = self.list_warehouses.currentItem()
        if current_item:
            self.selected_warehouse_id = current_item.data(Qt.ItemDataRole.UserRole)
            super().accept()

    def get_selected_warehouse_id(self):
        """Return selected warehouse ID."""
        return self.selected_warehouse_id
