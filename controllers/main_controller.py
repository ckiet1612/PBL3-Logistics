# controllers/main_controller.py
"""
Main Controller - Coordinator for sub-controllers.
Refactored from 700+ lines to modular architecture.
"""
from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtCore import Qt

from ui.main_window import MainWindow
from services.order_service import OrderService
from services.ocrspace_service import OCRSpaceService
from services.report_service import ReportService

# Import sub-controllers
from controllers.order_controller import OrderController
from controllers.filter_controller import FilterController
from controllers.undo_controller import UndoController
from controllers.context_menu_controller import ContextMenuController
from controllers.export_controller import ExportController


class MainController:
    """Main controller that coordinates sub-controllers."""

    def __init__(self, user_data=None, auth_service=None):
        self.user_data = user_data or {}
        self.auth_service = auth_service
        self.is_admin = self.user_data.get('is_admin', False)

        # Initialize Views and Services
        self.view = MainWindow(user_data=user_data, auth_service=auth_service)
        self.service = OrderService()
        self.ocr_service = OCRSpaceService()
        self.report_service = ReportService()

        # Initialize sub-controllers
        self.order_ctrl = OrderController(self.view, self.service, self)
        self.filter_ctrl = FilterController(self.view, self.service, self)
        self.undo_ctrl = UndoController(self.view, self.service, self)
        self.context_menu_ctrl = ContextMenuController(self.view, self.service, self)
        self.export_ctrl = ExportController(
            self.view, self.ocr_service, self.report_service, self
        )

        # Connect signals
        self._connect_signals()

        # Setup Undo/Redo shortcuts
        self.undo_ctrl.setup_undo_redo_shortcuts()

        # Load provinces for filter dropdown
        self.filter_ctrl.load_province_filter()

        # Initial load
        self.load_orders()
        self.view.show()

    def _connect_signals(self):
        """Connect all UI signals to sub-controller methods."""
        # Order operations
        self.view.btn_add.clicked.connect(self.order_ctrl.open_add_order_dialog)
        self.view.btn_refresh.clicked.connect(self.load_orders)

        # OCR and Export
        self.view.btn_scan_ai.clicked.connect(self.export_ctrl.scan_with_ocr)
        self.view.btn_export.clicked.connect(self.export_ctrl.export_data)

        # Hide buttons for Staff users
        if not self.is_admin:
            self.view.btn_export.setVisible(False)

        # Search and Filter
        self.view.search_input.returnPressed.connect(self.filter_ctrl.apply_filters)
        self.view.search_input.textChanged.connect(self.filter_ctrl.apply_filters)
        self.view.filter_status.currentTextChanged.connect(self.filter_ctrl.apply_filters)
        self.view.filter_time.currentTextChanged.connect(self.filter_ctrl.apply_filters)
        self.view.filter_province.currentTextChanged.connect(self.filter_ctrl.apply_filters)
        self.view.btn_clear_filter.clicked.connect(self.filter_ctrl.clear_filters)

        # Table interactions
        self.view.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.view.table.customContextMenuRequested.connect(
            self.context_menu_ctrl.show_context_menu
        )
        self.view.table.itemDoubleClicked.connect(self.order_ctrl.on_item_double_clicked)

    def load_orders(self, orders=None):
        """
        Fetch data, update Table AND update Dashboard.
        If orders is provided, use that list instead of fetching all.
        """
        if orders is None or not isinstance(orders, list):
            orders = self.service.get_all_orders()
            # Clear search input when refreshing
            self.view.search_input.clear()

        # Update Table
        self._update_table(orders)

        # Update Quick Stats
        self._update_stats(orders)

        # Update Dashboard Chart
        self.view.tab_dashboard.update_chart(orders)

    def _update_table(self, orders):
        """Update the orders table with data."""
        # Disable sorting while adding rows
        self.view.table.setSortingEnabled(False)
        self.view.table.setRowCount(0)

        # Status display mapping
        status_display_map = {
            'New': 'Mới tạo',
            'Processing': 'Đang xử lý',
            'Shipping': 'Đang giao',
            'Delivered': 'Đã giao',
            'Cancelled': 'Đã huỷ'
        }

        for row_idx, order in enumerate(orders):
            self.view.table.insertRow(row_idx)

            # Col 0: Mã đơn
            tracking_item = QTableWidgetItem(order.tracking_code)
            tracking_item.setData(Qt.ItemDataRole.UserRole, order.id)
            tracking_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.view.table.setItem(row_idx, 0, tracking_item)

            # Col 1: Trạng thái
            status_text = status_display_map.get(order.status, order.status)
            status_item = QTableWidgetItem(status_text)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.view.table.setItem(row_idx, 1, status_item)

            # Col 2: Người gửi → Người nhận
            sender = order.sender_name or "N/A"
            receiver = order.receiver_name or "N/A"
            self.view.table.setItem(row_idx, 2, QTableWidgetItem(f"{sender} → {receiver}"))

            # Col 3: Tuyến đường
            route = order.get_route_summary() if hasattr(order, 'get_route_summary') else "N/A → N/A"
            route_item = QTableWidgetItem(route)
            route_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.view.table.setItem(row_idx, 3, route_item)

            # Col 4: Số kiện / Trọng lượng
            package_info = (
                order.get_package_summary()
                if hasattr(order, 'get_package_summary')
                else f"1 kiện / {order.weight:.1f} kg"
            )
            pkg_item = QTableWidgetItem(package_info)
            pkg_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.view.table.setItem(row_idx, 4, pkg_item)

            # Col 5: Tổng phí
            total = order.get_total_cost() if hasattr(order, 'get_total_cost') else order.shipping_cost
            cost_text = f"{total:,.0f} VND"
            if hasattr(order, 'has_cod') and order.has_cod:
                cost_text += " (COD)"
            cost_item = QTableWidgetItem(cost_text)
            cost_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.view.table.setItem(row_idx, 5, cost_item)

            # Col 6: Thời gian tạo
            created_at = order.created_at.strftime("%d/%m/%Y %H:%M") if order.created_at else "N/A"
            time_item = QTableWidgetItem(created_at)
            time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.view.table.setItem(row_idx, 6, time_item)

        # Re-enable sorting
        self.view.table.setSortingEnabled(True)

    def _update_stats(self, orders):
        """Update the quick stats footer."""
        total_count = len(orders) if orders else 0
        new_count = sum(1 for o in orders if o.status == "New") if orders else 0
        processing_count = sum(1 for o in orders if o.status == "Processing") if orders else 0
        shipping_count = sum(1 for o in orders if o.status == "Shipping") if orders else 0
        delivered_count = sum(1 for o in orders if o.status == "Delivered") if orders else 0

        self.view.lbl_quick_stats.setText(
            f"📦 Tổng: {total_count} | 🆕 Mới: {new_count} | "
            f"⏳ Đang xử lý: {processing_count} | 🚚 Đang giao: {shipping_count} | "
            f"✅ Đã giao: {delivered_count}"
        )

    # Delegate methods for smart filter (called by sub-controllers)
    def _refresh_with_smart_filter(self, old_data, new_data):
        """Delegate to filter controller."""
        self.filter_ctrl.refresh_with_smart_filter(old_data, new_data)
