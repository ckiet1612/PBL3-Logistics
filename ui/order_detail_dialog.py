# ui/order_detail_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QScrollArea, QWidget, QFrame, QPushButton,
                              QGridLayout)
from PyQt6.QtCore import Qt

class OrderDetailDialog(QDialog):
    """Dialog to display all order information."""

    # Mapping for display labels
    ORDER_TYPE_LABELS = {'domestic': 'Nội địa', 'international': 'Quốc tế'}
    ITEM_TYPE_LABELS = {'normal': 'Thường', 'fragile': 'Dễ vỡ', 'frozen': 'Đông lạnh', 'dangerous': 'Nguy hiểm'}
    SERVICE_TYPE_LABELS = {'standard': 'Tiêu chuẩn', 'express': 'Nhanh', 'urgent': 'Hoả tốc'}
    PAYMENT_TYPE_LABELS = {'sender': 'Người gửi trả', 'receiver': 'Người nhận trả'}

    def __init__(self, order_data, parent=None):
        super().__init__(parent)
        self.order_data = order_data
        self.setWindowTitle(f"Chi tiết đơn hàng - {order_data.get('tracking_code', '')}")
        self.setMinimumSize(600, 700)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Header
        header = QLabel(f"📦 {self.order_data.get('tracking_code', 'N/A')}")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #2196F3;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll_layout.addWidget(header)

        # Status badge
        status = self.order_data.get('status', 'New')
        status_label = QLabel(f"Trạng thái: {status}")
        status_label.setStyleSheet(self.get_status_style(status))
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll_layout.addWidget(status_label)

        scroll_layout.addSpacing(20)

        # Timeline section (first)
        self.add_timeline_section(scroll_layout)

        # Sections
        self.add_section(scroll_layout, "📋 Thông tin đơn hàng", [
            ("Loại đơn", self.ORDER_TYPE_LABELS.get(self.order_data.get('order_type'), 'Nội địa')),
            ("Thời gian tạo", self.format_datetime(self.order_data.get('created_at'))),
        ])

        self.add_section(scroll_layout, "👤 Người gửi", [
            ("Họ tên", self.order_data.get('sender_name')),
            ("Số điện thoại", self.order_data.get('sender_phone')),
            ("Email", self.order_data.get('sender_email')),
            ("Địa chỉ", self.order_data.get('sender_address')),
            ("Tỉnh/Thành", self.order_data.get('sender_province')),
        ])

        self.add_section(scroll_layout, "📍 Người nhận", [
            ("Họ tên", self.order_data.get('receiver_name')),
            ("Số điện thoại", self.order_data.get('receiver_phone')),
            ("Email", self.order_data.get('receiver_email')),
            ("Địa chỉ", self.order_data.get('receiver_address')),
            ("Tỉnh/Thành", self.order_data.get('receiver_province')),
        ])

        self.add_section(scroll_layout, "📦 Thông tin hàng hoá", [
            ("Tên/Mô tả", self.order_data.get('item_name')),
            ("Loại hàng", self.ITEM_TYPE_LABELS.get(self.order_data.get('item_type'), 'Thường')),
            ("Số kiện", str(self.order_data.get('package_count', 1))),
            ("Trọng lượng", f"{self.order_data.get('weight', 0):.2f} kg"),
            ("Kích thước", self.order_data.get('dimensions')),
        ])

        self.add_section(scroll_layout, "🚚 Dịch vụ vận chuyển", [
            ("Loại dịch vụ", self.SERVICE_TYPE_LABELS.get(self.order_data.get('service_type'), 'Tiêu chuẩn')),
            ("Ghi chú giao hàng", self.order_data.get('delivery_note')),
        ])

        # Payment section with highlight
        has_cod = self.order_data.get('has_cod', False)
        cod_text = f"Có - {self.order_data.get('cod_amount', 0):,.0f} VND" if has_cod else "Không"
        shipping_cost = self.order_data.get('shipping_cost', 0)
        total_cost = shipping_cost + (self.order_data.get('cod_amount', 0) if has_cod else 0)

        self.add_section(scroll_layout, "💰 Thanh toán", [
            ("Hình thức thanh toán", self.PAYMENT_TYPE_LABELS.get(self.order_data.get('payment_type'), 'Người gửi trả')),
            ("Phí vận chuyển", f"{shipping_cost:,.0f} VND"),
            ("Thu hộ (COD)", cod_text),
            ("TỔNG CỘNG", f"{total_cost:,.0f} VND"),
        ])

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Close button
        btn_close = QPushButton("Đóng")
        btn_close.setMinimumHeight(40)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def add_section(self, layout, title, items):
        """Add a section with title and items."""
        # Section frame
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet("QFrame { background-color: #f5f5f5; border-radius: 8px; padding: 10px; }")
        frame_layout = QVBoxLayout(frame)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; margin-bottom: 10px;")
        frame_layout.addWidget(title_label)

        # Items grid
        grid = QGridLayout()
        grid.setColumnStretch(1, 1)

        for row, (label, value) in enumerate(items):
            label_widget = QLabel(f"{label}:")
            label_widget.setStyleSheet("font-weight: bold; color: #666;")

            value_text = str(value) if value else "—"
            value_widget = QLabel(value_text)
            value_widget.setWordWrap(True)

            # Highlight total
            if label == "TỔNG CỘNG":
                value_widget.setStyleSheet("font-weight: bold; font-size: 16px; color: #E91E63;")

            grid.addWidget(label_widget, row, 0, Qt.AlignmentFlag.AlignTop)
            grid.addWidget(value_widget, row, 1, Qt.AlignmentFlag.AlignTop)

        frame_layout.addLayout(grid)
        layout.addWidget(frame)
        layout.addSpacing(10)

    def format_datetime(self, dt):
        """Format datetime for display."""
        if dt:
            if isinstance(dt, str):
                return dt
            return dt.strftime("%d/%m/%Y %H:%M")
        return "—"

    def get_status_style(self, status):
        """Get style for status label."""
        colors = {
            'New': '#2196F3',
            'Shipping': '#FF9800',
            'Delivered': '#4CAF50',
            'Cancelled': '#F44336'
        }
        color = colors.get(status, '#666')
        return f"font-size: 14px; font-weight: bold; color: white; background-color: {color}; padding: 5px 15px; border-radius: 12px;"

    def add_timeline_section(self, layout):
        """Add timeline section showing status history."""
        from services.order_service import OrderService

        order_id = self.order_data.get('id')
        if not order_id:
            return

        service = OrderService()
        history = service.get_status_history(order_id)

        # Section frame
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet("QFrame { background-color: #fff3e0; border-radius: 8px; padding: 10px; }")
        frame_layout = QVBoxLayout(frame)

        # Title
        title_label = QLabel("📜 Lịch sử trạng thái")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; margin-bottom: 10px;")
        frame_layout.addWidget(title_label)

        if history:
            for entry in history:
                # Timeline item
                item_layout = QHBoxLayout()

                # Icon and status
                icon = entry.get_status_icon() if hasattr(entry, 'get_status_icon') else '📋'
                status_text = entry.get_status_display() if hasattr(entry, 'get_status_display') else entry.new_status

                status_label = QLabel(f"{icon} {status_text}")
                status_label.setStyleSheet("font-weight: bold; font-size: 13px;")
                item_layout.addWidget(status_label)

                item_layout.addStretch()

                # Timestamp
                time_str = entry.changed_at.strftime("%d/%m/%Y %H:%M") if entry.changed_at else "—"
                time_label = QLabel(time_str)
                time_label.setStyleSheet("color: #888; font-size: 12px;")
                item_layout.addWidget(time_label)

                frame_layout.addLayout(item_layout)

                # Changed by (if available)
                if entry.changed_by:
                    by_label = QLabel(f"   Bởi: {entry.changed_by}")
                    by_label.setStyleSheet("color: #666; font-size: 11px; margin-left: 20px;")
                    frame_layout.addWidget(by_label)

                # Note (if available)
                if entry.note:
                    note_label = QLabel(f"   📝 {entry.note}")
                    note_label.setStyleSheet("color: #555; font-size: 11px; font-style: italic;")
                    frame_layout.addWidget(note_label)
        else:
            # No history yet - show creation info
            created_at = self.format_datetime(self.order_data.get('created_at'))
            no_history = QLabel(f"🆕 Đơn hàng được tạo lúc {created_at}")
            no_history.setStyleSheet("color: #666; font-style: italic;")
            frame_layout.addWidget(no_history)

        layout.addWidget(frame)
        layout.addSpacing(10)
