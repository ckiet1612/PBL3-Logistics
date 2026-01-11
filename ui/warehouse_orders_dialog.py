# ui/warehouse_orders_dialog.py
from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QTableWidget, QTableWidgetItem,
                              QHeaderView)
from PyQt6.QtCore import Qt
from services.warehouse_service import WarehouseService
from ui.base_dialog import BaseDialog
from ui.constants import BUTTON_STYLE_NEUTRAL, HEADER_STYLE, INFO_STYLE, TABLE_STYLE


class WarehouseOrdersDialog(BaseDialog):
    """Dialog to display orders in a warehouse."""

    def __init__(self, parent=None, warehouse_id=None, warehouse_name=""):
        title = f"Đơn hàng trong kho: {warehouse_name}"
        super().__init__(parent, title=title, min_width=700, min_height=450)
        self.warehouse_id = warehouse_id
        self.warehouse_name = warehouse_name
        self.service = WarehouseService()
        self.setup_ui()
        self.load_orders()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_layout = QHBoxLayout()
        header = QLabel(f"🏭 {self.warehouse_name}")
        header.setStyleSheet(HEADER_STYLE)
        header_layout.addWidget(header)

        header_layout.addStretch()

        # Stats
        stats = self.service.get_warehouse_stats(self.warehouse_id)
        if stats:
            stats_label = QLabel(f"📦 {stats['order_count']}/{stats['capacity']} ({stats['capacity_pct']:.0f}%)")
            stats_label.setStyleSheet(INFO_STYLE)
            header_layout.addWidget(stats_label)

        layout.addLayout(header_layout)

        # Orders table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Mã đơn", "Người gửi", "Người nhận", "Trạng thái", "Ngày tạo"
        ])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(35)
        self.table.setStyleSheet(TABLE_STYLE)
        layout.addWidget(self.table)

        # Footer
        footer_layout = QHBoxLayout()

        self.lbl_count = QLabel("Tổng: 0 đơn")
        self.lbl_count.setStyleSheet(INFO_STYLE)
        footer_layout.addWidget(self.lbl_count)

        footer_layout.addStretch()

        btn_close = QPushButton("Đóng")
        btn_close.setStyleSheet(BUTTON_STYLE_NEUTRAL)
        btn_close.clicked.connect(self.close)
        footer_layout.addWidget(btn_close)

        layout.addLayout(footer_layout)

    def load_orders(self):
        """Load orders in this warehouse."""
        orders = self.service.get_orders_in_warehouse(self.warehouse_id)

        self.table.setRowCount(0)
        for row_idx, order in enumerate(orders):
            self.table.insertRow(row_idx)

            # Tracking code
            self.table.setItem(row_idx, 0, QTableWidgetItem(order.tracking_code))

            # Sender
            self.table.setItem(row_idx, 1, QTableWidgetItem(order.sender_name or "N/A"))

            # Receiver
            self.table.setItem(row_idx, 2, QTableWidgetItem(order.receiver_name or "N/A"))

            # Status
            status_item = QTableWidgetItem(order.status or "N/A")
            if order.status == "Delivered":
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            elif order.status == "Cancelled":
                status_item.setForeground(Qt.GlobalColor.red)
            self.table.setItem(row_idx, 3, status_item)

            # Created at
            created_at = order.created_at.strftime("%d/%m/%Y") if order.created_at else "N/A"
            self.table.setItem(row_idx, 4, QTableWidgetItem(created_at))

        self.lbl_count.setText(f"Tổng: {len(orders)} đơn")
