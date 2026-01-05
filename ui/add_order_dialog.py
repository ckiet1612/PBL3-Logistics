# ui/add_order_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QHBoxLayout,
                             QLineEdit, QDialogButtonBox, QDoubleSpinBox, 
                             QCheckBox, QComboBox, QSpinBox, QTextEdit,
                             QTabWidget, QWidget, QLabel, QScrollArea, QCompleter,
                             QPushButton)
from PyQt6.QtCore import Qt
from services.transport_service import TransportService
from services.ward_service import WardService

# Vietnam provinces list
VIETNAM_PROVINCES = [
    "", "Hà Nội", "TP. Hồ Chí Minh", "Hải Phòng", "Đà Nẵng", "Cần Thơ", "Huế",
    "Cao Bằng", "Điện Biên", "Lai Châu", "Sơn La", "Lạng Sơn", "Quảng Ninh",
    "Thanh Hóa", "Nghệ An", "Hà Tĩnh", "Tuyên Quang", "Lào Cai", "Thái Nguyên",
    "Phú Thọ", "Bắc Ninh", "Hưng Yên", "Ninh Bình", "Quảng Trị", "Quảng Ngãi",
    "Gia Lai", "Khánh Hòa", "Lâm Đồng", "Đắk Lắk", "Đồng Nai", "Tây Ninh",
    "Vĩnh Long", "Đồng Tháp", "Cà Mau", "An Giang"
]

class AddOrderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Thêm đơn hàng mới")
        self.setMinimumSize(650, 600)
        
        self.transport_service = TransportService()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Tab widget for organizing fields
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Tab 1: Basic Info
        self.setup_basic_tab()
        
        # Tab 2: Sender Info
        self.setup_sender_tab()
        
        # Tab 3: Receiver Info
        self.setup_receiver_tab()
        
        # Tab 4: Package Info
        self.setup_package_tab()
        
        # Tab 5: Service & Payment
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
        """Tab for basic order information."""
        tab = QWidget()
        form = QFormLayout(tab)
        form.setSpacing(10)
        
        # Tracking Code
        self.txt_tracking = QLineEdit()
        self.txt_tracking.setPlaceholderText("VD: #DH001")
        form.addRow("Mã vận đơn *:", self.txt_tracking)
        
        # Order Type
        self.cmb_order_type = QComboBox()
        self.cmb_order_type.addItems(["Nội địa", "Quốc tế"])
        form.addRow("Loại đơn:", self.cmb_order_type)
        
        # Warehouse
        self.cmb_warehouse = QComboBox()
        self.cmb_warehouse.addItem("-- Chọn kho --", None)
        self._load_warehouses()
        form.addRow("Kho lưu trữ:", self.cmb_warehouse)
        
        self.tabs.addTab(tab, "📋 Cơ bản")

    def setup_sender_tab(self):
        """Tab for sender information."""
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
        self.cmb_sender_province.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        completer_sender = QCompleter(VIETNAM_PROVINCES)
        completer_sender.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer_sender.setFilterMode(Qt.MatchFlag.MatchContains)
        self.cmb_sender_province.setCompleter(completer_sender)
        self.cmb_sender_province.currentTextChanged.connect(self.on_sender_province_changed)
        self.cmb_sender_province.currentTextChanged.connect(self.auto_calculate_cost)
        form.addRow("Tỉnh/Thành:", self.cmb_sender_province)
        
        # Ward/Commune dropdown (dependent on province)
        self.cmb_sender_ward = QComboBox()
        self.cmb_sender_ward.setEditable(True)
        self.cmb_sender_ward.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.cmb_sender_ward.setMinimumWidth(250)
        form.addRow("Xã/Phường:", self.cmb_sender_ward)
        
        self.tabs.addTab(tab, "👤 Người gửi")

    def setup_receiver_tab(self):
        """Tab for receiver information."""
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
        self.cmb_receiver_province.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        completer_receiver = QCompleter(VIETNAM_PROVINCES)
        completer_receiver.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer_receiver.setFilterMode(Qt.MatchFlag.MatchContains)
        self.cmb_receiver_province.setCompleter(completer_receiver)
        self.cmb_receiver_province.currentTextChanged.connect(self.on_receiver_province_changed)
        self.cmb_receiver_province.currentTextChanged.connect(self.auto_calculate_cost)
        form.addRow("Tỉnh/Thành:", self.cmb_receiver_province)
        
        # Ward/Commune dropdown (dependent on province)
        self.cmb_receiver_ward = QComboBox()
        self.cmb_receiver_ward.setEditable(True)
        self.cmb_receiver_ward.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.cmb_receiver_ward.setMinimumWidth(250)
        form.addRow("Xã/Phường:", self.cmb_receiver_ward)
        
        self.tabs.addTab(tab, "📍 Người nhận")

    def setup_package_tab(self):
        """Tab for package information."""
        tab = QWidget()
        form = QFormLayout(tab)
        form.setSpacing(10)
        
        self.txt_item_name = QLineEdit()
        self.txt_item_name.setPlaceholderText("Mô tả hàng hoá")
        form.addRow("Tên hàng:", self.txt_item_name)
        
        self.cmb_item_type = QComboBox()
        self.cmb_item_type.addItems(["Thường", "Dễ vỡ", "Đông lạnh", "Nguy hiểm"])
        form.addRow("Loại hàng:", self.cmb_item_type)
        
        self.spin_package_count = QSpinBox()
        self.spin_package_count.setRange(1, 999)
        self.spin_package_count.setValue(1)
        form.addRow("Số kiện:", self.spin_package_count)
        
        self.spin_weight = QDoubleSpinBox()
        self.spin_weight.setRange(0, 10000)
        self.spin_weight.setSuffix(" kg")
        self.spin_weight.setDecimals(2)
        self.spin_weight.valueChanged.connect(self.auto_calculate_cost)
        form.addRow("Trọng lượng:", self.spin_weight)
        
        self.txt_dimensions = QLineEdit()
        self.txt_dimensions.setPlaceholderText("VD: 30x20x15 cm")
        form.addRow("Kích thước:", self.txt_dimensions)
        
        self.txt_delivery_note = QTextEdit()
        self.txt_delivery_note.setMaximumHeight(60)
        self.txt_delivery_note.setPlaceholderText("Ghi chú cho shipper...")
        form.addRow("Ghi chú giao hàng:", self.txt_delivery_note)
        
        self.tabs.addTab(tab, "📦 Hàng hoá")

    def setup_service_tab(self):
        """Tab for service and payment information."""
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
        
        # Auto-calc button
        from PyQt6.QtWidgets import QHBoxLayout
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
        
        # COD section
        self.chk_cod = QCheckBox("Có thu hộ (COD)")
        self.chk_cod.stateChanged.connect(self.on_cod_changed)
        form.addRow("", self.chk_cod)
        
        self.spin_cod_amount = QDoubleSpinBox()
        self.spin_cod_amount.setRange(0, 100000000)
        self.spin_cod_amount.setSingleStep(10000)
        self.spin_cod_amount.setSuffix(" VND")
        self.spin_cod_amount.setDecimals(0)
        self.spin_cod_amount.setEnabled(False)
        form.addRow("Số tiền thu hộ:", self.spin_cod_amount)
        
        self.tabs.addTab(tab, "💲 Thanh toán")

    def on_cod_changed(self, state):
        """Enable/disable COD amount input."""
        self.spin_cod_amount.setEnabled(state == Qt.CheckState.Checked.value)
        if state != Qt.CheckState.Checked.value:
            self.spin_cod_amount.setValue(0)

    def get_data(self):
        """Return all form data as dictionary."""
        item_type_map = {"Thường": "normal", "Dễ vỡ": "fragile", "Đông lạnh": "frozen", "Nguy hiểm": "dangerous"}
        service_type_map = {"Tiêu chuẩn": "standard", "Nhanh": "express", "Hoả tốc": "urgent"}
        payment_type_map = {"Người gửi trả": "sender", "Người nhận trả": "receiver"}
        
        return {
            "tracking_code": self.txt_tracking.text().strip(),
            "order_type": "domestic" if self.cmb_order_type.currentIndex() == 0 else "international",
            "current_warehouse_id": self.cmb_warehouse.currentData(),
            "sender_name": self.txt_sender_name.text().strip(),
            "sender_phone": self.txt_sender_phone.text().strip(),
            "sender_email": self.txt_sender_email.text().strip(),
            "sender_address": self.txt_sender_address.toPlainText().strip(),
            "sender_province": self.cmb_sender_province.currentText(),
            "sender_ward": self.cmb_sender_ward.currentText(),
            "receiver_name": self.txt_receiver_name.text().strip(),
            "receiver_phone": self.txt_receiver_phone.text().strip(),
            "receiver_email": self.txt_receiver_email.text().strip(),
            "receiver_address": self.txt_receiver_address.toPlainText().strip(),
            "receiver_province": self.cmb_receiver_province.currentText(),
            "receiver_ward": self.cmb_receiver_ward.currentText(),
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

    def fill_data(self, data):
        """Auto-fill form with extracted data (from Gemini AI)."""
        if not data:
            return
        
        # --- SENDER ---
        if data.get("sender_name"):
            self.txt_sender_name.setText(data["sender_name"])
        if data.get("sender_phone"):
            self.txt_sender_phone.setText(data["sender_phone"])
        if data.get("sender_email"):
            self.txt_sender_email.setText(data["sender_email"])
        if data.get("sender_address"):
            self.txt_sender_address.setPlainText(data["sender_address"])
        if data.get("sender_province"):
            self.set_combo_value(self.cmb_sender_province, data["sender_province"])
        
        # --- RECEIVER ---
        if data.get("receiver_name"):
            self.txt_receiver_name.setText(data["receiver_name"])
        if data.get("receiver_phone"):
            self.txt_receiver_phone.setText(data["receiver_phone"])
        if data.get("receiver_email"):
            self.txt_receiver_email.setText(data["receiver_email"])
        if data.get("receiver_address"):
            self.txt_receiver_address.setPlainText(data["receiver_address"])
        if data.get("receiver_province"):
            self.set_combo_value(self.cmb_receiver_province, data["receiver_province"])
        
        # --- PACKAGE ---
        if data.get("item_name"):
            self.txt_item_name.setText(data["item_name"])
        if data.get("package_count") and data["package_count"] > 0:
            self.spin_package_count.setValue(int(data["package_count"]))
        if data.get("dimensions"):
            self.txt_dimensions.setText(data["dimensions"])
        if data.get("delivery_note"):
            self.txt_delivery_note.setPlainText(data["delivery_note"])
        
        # --- WEIGHT ---
        if data.get("weight") and data["weight"] > 0:
            self.spin_weight.setValue(float(data["weight"]))
        
        # --- COST ---
        if data.get("shipping_cost") and data["shipping_cost"] > 0:
            self.chk_auto_calc.setChecked(False)
            self.spin_cost.setValue(float(data["shipping_cost"]))
        else:
            self.chk_auto_calc.setChecked(True)
        
        # --- COD ---
        if data.get("has_cod"):
            self.chk_cod.setChecked(True)
            if data.get("cod_amount") and data["cod_amount"] > 0:
                self.spin_cod_amount.setValue(float(data["cod_amount"]))
        
        # --- AUTO TRACKING CODE ---
        import random
        if not self.txt_tracking.text():
            self.txt_tracking.setText(f"#DH{random.randint(1000,9999)}")

    def set_combo_value(self, combo, value):
        """Set combo box value, adding if not exists."""
        idx = combo.findText(value)
        if idx >= 0:
            combo.setCurrentIndex(idx)
        else:
            combo.setCurrentText(value)

    def on_sender_province_changed(self, province):
        """Update sender ward dropdown when province changes."""
        self.cmb_sender_ward.clear()
        if province:
            wards = WardService().get_wards(province)
            if wards:
                self.cmb_sender_ward.addItems([""] + wards)
                # Add completer for search
                completer = QCompleter(wards)
                completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
                completer.setFilterMode(Qt.MatchFlag.MatchContains)
                self.cmb_sender_ward.setCompleter(completer)

    def on_receiver_province_changed(self, province):
        """Update receiver ward dropdown when province changes."""
        self.cmb_receiver_ward.clear()
        if province:
            wards = WardService().get_wards(province)
            if wards:
                self.cmb_receiver_ward.addItems([""] + wards)
                # Add completer for search
                completer = QCompleter(wards)
                completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
                completer.setFilterMode(Qt.MatchFlag.MatchContains)
                self.cmb_receiver_ward.setCompleter(completer)

    def _load_warehouses(self):
        """Load warehouses into dropdown."""
        from services.warehouse_service import WarehouseService
        warehouses = WarehouseService().get_all_warehouses()
        for wh in warehouses:
            if wh.status == 'active':
                self.cmb_warehouse.addItem(f"{wh.name} ({wh.province})", wh.id)

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