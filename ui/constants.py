# ui/constants.py
"""
Shared constants for UI components to reduce code duplication.
"""

# Vietnamese provinces list (empty string at start for dropdown default)
VIETNAM_PROVINCES = [
    "", "Hà Nội", "TP. Hồ Chí Minh", "Đà Nẵng", "Hải Phòng", "Cần Thơ",
    "Bình Dương", "Bà Rịa - Vũng Tàu", "Bắc Giang", "Hà Nam", "Hải Dương",
    "Hoà Bình", "Nam Định", "Thái Bình", "Vĩnh Phúc", "Yên Bái", "Bắc Kạn",
    "Cao Bằng", "Điện Biên", "Lai Châu", "Sơn La", "Lạng Sơn", "Quảng Ninh",
    "Thanh Hóa", "Nghệ An", "Hà Tĩnh", "Tuyên Quang", "Lào Cai", "Thái Nguyên",
    "Phú Thọ", "Bắc Ninh", "Hưng Yên", "Ninh Bình", "Quảng Trị", "Quảng Ngãi",
    "Gia Lai", "Khánh Hòa", "Lâm Đồng", "Đắk Lắk", "Đồng Nai", "Tây Ninh",
    "Vĩnh Long", "Đồng Tháp", "Cà Mau", "An Giang", "Huế", "Quảng Bình",
    "Quảng Nam", "Bình Định", "Phú Yên", "Ninh Thuận", "Bình Thuận",
    "Kon Tum", "Đắk Nông", "Bình Phước", "Long An", "Tiền Giang",
    "Bến Tre", "Trà Vinh", "Sóc Trăng", "Bạc Liêu", "Hậu Giang", "Kiên Giang"
]

# Item type mappings
ITEM_TYPE_MAP = {
    "Thường": "normal",
    "Dễ vỡ": "fragile",
    "Đông lạnh": "frozen",
    "Nguy hiểm": "dangerous"
}

ITEM_TYPE_REVERSE_MAP = {v: k for k, v in ITEM_TYPE_MAP.items()}

# Service type mappings
SERVICE_TYPE_MAP = {
    "Tiêu chuẩn": "standard",
    "Nhanh": "express",
    "Hoả tốc": "urgent"
}

SERVICE_TYPE_REVERSE_MAP = {v: k for k, v in SERVICE_TYPE_MAP.items()}

# Payment type mappings
PAYMENT_TYPE_MAP = {
    "Người gửi trả": "sender",
    "Người nhận trả": "receiver"
}

PAYMENT_TYPE_REVERSE_MAP = {v: k for k, v in PAYMENT_TYPE_MAP.items()}

# Shared button styles
BUTTON_STYLE_GREEN = """
    QPushButton {
        background-color: #4CAF50;
        color: white;
        padding: 8px 16px;
        border-radius: 4px;
    }
    QPushButton:hover { background-color: #45a049; }
"""

BUTTON_STYLE_GRAY = """
    QPushButton {
        background-color: #607D8B;
        color: white;
        padding: 8px 16px;
        border-radius: 4px;
    }
    QPushButton:hover { background-color: #546E7A; }
"""

BUTTON_STYLE_RED = """
    QPushButton {
        background-color: #f44336;
        color: white;
        padding: 8px 16px;
        border-radius: 4px;
    }
    QPushButton:hover { background-color: #d32f2f; }
"""

# Shared table styles
TABLE_STYLE = """
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
"""
