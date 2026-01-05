# ui/edit_order_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QHBoxLayout,
                             QLineEdit, QDialogButtonBox, QDoubleSpinBox, 
                             QCheckBox, QComboBox, QSpinBox, QTextEdit,
                             QTabWidget, QWidget, QLabel, QPushButton)
from PyQt6.QtCore import Qt

# Vietnam provinces list
VIETNAM_PROVINCES = [
    "", "An Giang", "Bà Rịa - Vũng Tàu", "Bắc Giang", "Bắc Kạn", "Bạc Liêu",
    "Bắc Ninh", "Bến Tre", "Bình Định", "Bình Dương", "Bình Phước", "Bình Thuận",
    "Cà Mau", "Cần Thơ", "Cao Bằng", "Đà Nẵng", "Đắk Lắk", "Đắk Nông",
    "Điện Biên", "Đồng Nai", "Đồng Tháp", "Gia Lai", "Hà Giang", "Hà Nam",
    "Hà Nội", "Hà Tĩnh", "Hải Dương", "Hải Phòng", "Hậu Giang", "Hòa Bình",
    "Hưng Yên", "Khánh Hòa", "Kiên Giang", "Kon Tum", "Lai Châu", "Lâm Đồng",
    "Lạng Sơn", "Lào Cai", "Long An", "Nam Định", "Nghệ An", "Ninh Bình",
    "Ninh Thuận", "Phú Thọ", "Phú Yên", "Quảng Bình", "Quảng Nam", "Quảng Ngãi",
    "Quảng Ninh", "Quảng Trị", "Sóc Trăng", "Sơn La", "Tây Ninh", "Thái Bình",
    "Thái Nguyên", "Thanh Hóa", "Thừa Thiên Huế", "Tiền Giang", "TP. Hồ Chí Minh",
    "Trà Vinh", "Tuyên Quang", "Vĩnh Long", "Vĩnh Phúc", "Yên Bái"
]

class EditOrderDialog(QDialog):
    def __init__(self, order_data, parent=None):
        super().__init__(parent)
        self.order_data = order_data
        self.setWindowTitle(f"Sửa đơn hàng - {order_data.get('tracking_code', '')}")
        self.setMinimumSize(650, 600)
        
        self.setup_ui()
        self.fill_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel(f"✏️ Chỉnh sửa đơn hàng")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        self.setup_basic_tab()
        self.setup_sender_tab()
        self.setup_receiver_tab()
        self.setup_package_tab()
        self.setup_service_tab()
        
        # Buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | 
            QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.button(QDialogButtonBox.StandardButton.Save).setText("Lưu")
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Huỷ")
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def setup_basic_tab(self):
        tab = QWidget()
        form = QFormLayout(tab)
        form.setSpacing(10)
        
        self.txt_tracking = QLineEdit()
        form.addRow("Mã vận đơn *:", self.txt_tracking)
        
        self.cmb_order_type = QComboBox()
        self.cmb_order_type.addItems(["Nội địa", "Quốc tế"])
        form.addRow("Loại đơn:", self.cmb_order_type)
        
        self.tabs.addTab(tab, "📋 Cơ bản")

    def setup_sender_tab(self):
        tab = QWidget()
        form = QFormLayout(tab)
        form.setSpacing(10)
        
        self.txt_sender_name = QLineEdit()
        form.addRow("Họ tên:", self.txt_sender_name)
        
        self.txt_sender_phone = QLineEdit()
        form.addRow("Số điện thoại:", self.txt_sender_phone)
        
        self.txt_sender_email = QLineEdit()
        form.addRow("Email:", self.txt_sender_email)
        
        self.txt_sender_address = QTextEdit()
        self.txt_sender_address.setMaximumHeight(60)
        form.addRow("Địa chỉ:", self.txt_sender_address)
        
        self.cmb_sender_province = QComboBox()
        self.cmb_sender_province.addItems(VIETNAM_PROVINCES)
        self.cmb_sender_province.setEditable(True)
        self.cmb_sender_province.currentTextChanged.connect(self.auto_calculate_cost)
        form.addRow("Tỉnh/Thành:", self.cmb_sender_province)
        
        self.tabs.addTab(tab, "👤 Người gửi")

    def setup_receiver_tab(self):
        tab = QWidget()
        form = QFormLayout(tab)
        form.setSpacing(10)
        
        self.txt_receiver_name = QLineEdit()
        form.addRow("Họ tên:", self.txt_receiver_name)
        
        self.txt_receiver_phone = QLineEdit()
        form.addRow("Số điện thoại:", self.txt_receiver_phone)
        
        self.txt_receiver_email = QLineEdit()
        form.addRow("Email:", self.txt_receiver_email)
        
        self.txt_receiver_address = QTextEdit()
        self.txt_receiver_address.setMaximumHeight(60)
        form.addRow("Địa chỉ:", self.txt_receiver_address)
        
        self.cmb_receiver_province = QComboBox()
        self.cmb_receiver_province.addItems(VIETNAM_PROVINCES)
        self.cmb_receiver_province.setEditable(True)
        self.cmb_receiver_province.currentTextChanged.connect(self.auto_calculate_cost)
        form.addRow("Tỉnh/Thành:", self.cmb_receiver_province)
        
        self.tabs.addTab(tab, "📍 Người nhận")

    def setup_package_tab(self):
        tab = QWidget()
        form = QFormLayout(tab)
        form.setSpacing(10)
        
        self.txt_item_name = QLineEdit()
        form.addRow("Tên hàng:", self.txt_item_name)
        
        self.cmb_item_type = QComboBox()
        self.cmb_item_type.addItems(["Thường", "Dễ vỡ", "Đông lạnh", "Nguy hiểm"])
        form.addRow("Loại hàng:", self.cmb_item_type)
        
        self.spin_package_count = QSpinBox()
        self.spin_package_count.setRange(1, 999)
        form.addRow("Số kiện:", self.spin_package_count)
        
        self.spin_weight = QDoubleSpinBox()
        self.spin_weight.setRange(0, 10000)
        self.spin_weight.setSuffix(" kg")
        self.spin_weight.setDecimals(2)
        self.spin_weight.valueChanged.connect(self.auto_calculate_cost)
        form.addRow("Trọng lượng:", self.spin_weight)
        
        self.txt_dimensions = QLineEdit()
        form.addRow("Kích thước:", self.txt_dimensions)
        
        self.txt_delivery_note = QTextEdit()
        self.txt_delivery_note.setMaximumHeight(60)
        form.addRow("Ghi chú giao hàng:", self.txt_delivery_note)
        
        self.tabs.addTab(tab, "📦 Hàng hoá")

    def setup_service_tab(self):
        tab = QWidget()
        form = QFormLayout(tab)
        form.setSpacing(10)
        
        self.cmb_service_type = QComboBox()
        self.cmb_service_type.addItems(["Tiêu chuẩn", "Nhanh", "Hoả tốc"])
        form.addRow("Dịch vụ:", self.cmb_service_type)
        
        self.cmb_payment_type = QComboBox()
        self.cmb_payment_type.addItems(["Người gửi trả", "Người nhận trả"])
        form.addRow("Thanh toán:", self.cmb_payment_type)
        
        # Route info label
        self.lbl_route_info = QLabel("Tuyến: -- → --")
        self.lbl_route_info.setStyleSheet("color: #666; font-style: italic;")
        form.addRow("", self.lbl_route_info)
        
        # Auto-calc button with cost
        cost_layout = QHBoxLayout()
        self.spin_cost = QDoubleSpinBox()
        self.spin_cost.setRange(0, 100000000)
        self.spin_cost.setSingleStep(1000)
        self.spin_cost.setSuffix(" VND")
        self.spin_cost.setDecimals(0)
        cost_layout.addWidget(self.spin_cost)
        
        self.btn_auto_calc = QPushButton("⚡ Tính phí")
        self.btn_auto_calc.setStyleSheet("background-color: #2196F3; color: white; padding: 5px 10px;")
        self.btn_auto_calc.clicked.connect(self.auto_calculate_cost)
        cost_layout.addWidget(self.btn_auto_calc)
        form.addRow("Phí vận chuyển:", cost_layout)
        
        self.chk_cod = QCheckBox("Có thu hộ (COD)")
        self.chk_cod.stateChanged.connect(self.on_cod_changed)
        form.addRow("", self.chk_cod)
        
        self.spin_cod_amount = QDoubleSpinBox()
        self.spin_cod_amount.setRange(0, 100000000)
        self.spin_cod_amount.setSingleStep(10000)
        self.spin_cod_amount.setSuffix(" VND")
        self.spin_cod_amount.setDecimals(0)
        form.addRow("Số tiền thu hộ:", self.spin_cod_amount)
        
        self.tabs.addTab(tab, "💲 Thanh toán")

    def on_cod_changed(self, state):
        self.spin_cod_amount.setEnabled(state == Qt.CheckState.Checked.value)

    def auto_calculate_cost(self):
        """Calculate shipping cost based on route and weight."""
        from services.route_service import RouteService
        
        origin = self.cmb_sender_province.currentText()
        dest = self.cmb_receiver_province.currentText()
        weight = self.spin_weight.value()
        
        if not origin or not dest:
            self.lbl_route_info.setText("Tuyến: Chưa chọn tỉnh gửi/nhận")
            self.lbl_route_info.setStyleSheet("color: #f44336; font-style: italic;")
            return
        
        self.lbl_route_info.setText(f"Tuyến: {origin} → {dest}")
        
        route_service = RouteService()
        route = route_service.find_route(origin, dest)
        
        if route:
            cost = route.calculate_shipping_cost(weight)
            self.spin_cost.setValue(cost)
            self.lbl_route_info.setText(f"Tuyến: {origin} → {dest} ({route.distance_km:.0f}km)")
            self.lbl_route_info.setStyleSheet("color: #4CAF50; font-style: italic;")
        else:
            # Default cost if no route found
            default_cost = weight * 10000  # 10,000 VND/kg
            self.spin_cost.setValue(default_cost)
            self.lbl_route_info.setText(f"Tuyến: {origin} → {dest} (Chưa có giá cước)")
            self.lbl_route_info.setStyleSheet("color: #FF9800; font-style: italic;")

    def fill_data(self):
        """Fill form with existing order data."""
        data = self.order_data
        
        # Basic
        self.txt_tracking.setText(data.get('tracking_code', ''))
        self.cmb_order_type.setCurrentIndex(0 if data.get('order_type') == 'domestic' else 1)
        
        # Sender
        self.txt_sender_name.setText(data.get('sender_name', ''))
        self.txt_sender_phone.setText(data.get('sender_phone', ''))
        self.txt_sender_email.setText(data.get('sender_email', ''))
        self.txt_sender_address.setPlainText(data.get('sender_address', ''))
        self.set_combo_value(self.cmb_sender_province, data.get('sender_province', ''))
        
        # Receiver
        self.txt_receiver_name.setText(data.get('receiver_name', ''))
        self.txt_receiver_phone.setText(data.get('receiver_phone', ''))
        self.txt_receiver_email.setText(data.get('receiver_email', ''))
        self.txt_receiver_address.setPlainText(data.get('receiver_address', ''))
        self.set_combo_value(self.cmb_receiver_province, data.get('receiver_province', ''))
        
        # Package
        self.txt_item_name.setText(data.get('item_name', ''))
        item_type_idx = {"normal": 0, "fragile": 1, "frozen": 2, "dangerous": 3}.get(data.get('item_type', 'normal'), 0)
        self.cmb_item_type.setCurrentIndex(item_type_idx)
        self.spin_package_count.setValue(data.get('package_count', 1))
        self.spin_weight.setValue(data.get('weight', 0))
        self.txt_dimensions.setText(data.get('dimensions', ''))
        self.txt_delivery_note.setPlainText(data.get('delivery_note', ''))
        
        # Service
        service_idx = {"standard": 0, "express": 1, "urgent": 2}.get(data.get('service_type', 'standard'), 0)
        self.cmb_service_type.setCurrentIndex(service_idx)
        payment_idx = {"sender": 0, "receiver": 1}.get(data.get('payment_type', 'sender'), 0)
        self.cmb_payment_type.setCurrentIndex(payment_idx)
        self.spin_cost.setValue(data.get('shipping_cost', 0))
        
        # COD
        has_cod = data.get('has_cod', False)
        self.chk_cod.setChecked(has_cod)
        self.spin_cod_amount.setEnabled(has_cod)
        self.spin_cod_amount.setValue(data.get('cod_amount', 0))

    def set_combo_value(self, combo, value):
        """Set combo box value, adding if not exists."""
        idx = combo.findText(value)
        if idx >= 0:
            combo.setCurrentIndex(idx)
        else:
            combo.setCurrentText(value)

    def get_data(self):
        """Return all form data as dictionary."""
        item_type_map = {"Thường": "normal", "Dễ vỡ": "fragile", "Đông lạnh": "frozen", "Nguy hiểm": "dangerous"}
        service_type_map = {"Tiêu chuẩn": "standard", "Nhanh": "express", "Hoả tốc": "urgent"}
        payment_type_map = {"Người gửi trả": "sender", "Người nhận trả": "receiver"}
        
        return {
            "tracking_code": self.txt_tracking.text().strip(),
            "order_type": "domestic" if self.cmb_order_type.currentIndex() == 0 else "international",
            "sender_name": self.txt_sender_name.text().strip(),
            "sender_phone": self.txt_sender_phone.text().strip(),
            "sender_email": self.txt_sender_email.text().strip(),
            "sender_address": self.txt_sender_address.toPlainText().strip(),
            "sender_province": self.cmb_sender_province.currentText(),
            "receiver_name": self.txt_receiver_name.text().strip(),
            "receiver_phone": self.txt_receiver_phone.text().strip(),
            "receiver_email": self.txt_receiver_email.text().strip(),
            "receiver_address": self.txt_receiver_address.toPlainText().strip(),
            "receiver_province": self.cmb_receiver_province.currentText(),
            "item_name": self.txt_item_name.text().strip(),
            "item_type": item_type_map.get(self.cmb_item_type.currentText(), "normal"),
            "package_count": self.spin_package_count.value(),
            "weight": self.spin_weight.value(),
            "dimensions": self.txt_dimensions.text().strip(),
            "delivery_note": self.txt_delivery_note.toPlainText().strip(),
            "service_type": service_type_map.get(self.cmb_service_type.currentText(), "standard"),
            "payment_type": payment_type_map.get(self.cmb_payment_type.currentText(), "sender"),
            "shipping_cost": self.spin_cost.value(),
            "has_cod": self.chk_cod.isChecked(),
            "cod_amount": self.spin_cod_amount.value() if self.chk_cod.isChecked() else 0
        }
