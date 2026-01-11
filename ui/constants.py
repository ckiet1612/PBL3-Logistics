# ui/constants.py
"""
Shared constants for UI components to reduce code duplication.
"""

# Vietnamese provinces list based on province_wards.json (34 provinces with ward data)
# Major cities first, then alphabetically
VIETNAM_PROVINCES = [
    "", "Hà Nội", "TP. Hồ Chí Minh", "Đà Nẵng", "Hải Phòng", "Cần Thơ", "Huế",
    "An Giang", "Bắc Ninh", "Cà Mau", "Cao Bằng", "Điện Biên", "Đắk Lắk",
    "Đồng Nai", "Đồng Tháp", "Gia Lai", "Hà Tĩnh", "Hưng Yên", "Khánh Hòa",
    "Lai Châu", "Lâm Đồng", "Lạng Sơn", "Lào Cai", "Nghệ An", "Ninh Bình",
    "Phú Thọ", "Quảng Ngãi", "Quảng Ninh", "Quảng Trị", "Sơn La", "Tây Ninh",
    "Thái Nguyên", "Thanh Hóa", "Tuyên Quang", "Vĩnh Long"
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

# ============ BUTTON STYLES ============

# Primary button (Green - for main actions like Save, Add)
BUTTON_STYLE_PRIMARY = """
    QPushButton {
        background-color: #4CAF50;
        color: white;
        padding: 8px 16px;
        border-radius: 4px;
        font-weight: bold;
    }
    QPushButton:hover { background-color: #45a049; }
"""

# Alias for backward compatibility
BUTTON_STYLE_GREEN = BUTTON_STYLE_PRIMARY

# Secondary button (Blue - for info actions)
BUTTON_STYLE_SECONDARY = """
    QPushButton {
        background-color: #2196F3;
        color: white;
        padding: 8px 16px;
        border-radius: 4px;
    }
    QPushButton:hover { background-color: #1976D2; }
"""

# Danger button (Red - for delete, cancel)
BUTTON_STYLE_DANGER = """
    QPushButton {
        background-color: #f44336;
        color: white;
        padding: 8px 16px;
        border-radius: 4px;
    }
    QPushButton:hover { background-color: #d32f2f; }
"""

# Alias for backward compatibility
BUTTON_STYLE_RED = BUTTON_STYLE_DANGER

# Neutral button (Gray - for close, cancel)
BUTTON_STYLE_NEUTRAL = """
    QPushButton {
        background-color: #607D8B;
        color: white;
        padding: 8px 16px;
        border-radius: 4px;
    }
    QPushButton:hover { background-color: #546E7A; }
"""

# Alias for backward compatibility
BUTTON_STYLE_GRAY = BUTTON_STYLE_NEUTRAL

# Warning button (Orange)
BUTTON_STYLE_WARNING = """
    QPushButton {
        background-color: #FF9800;
        color: white;
        padding: 8px 16px;
        border-radius: 4px;
    }
    QPushButton:hover { background-color: #F57C00; }
"""

# Small secondary button (Blue - for inline actions like Calculate)
BUTTON_STYLE_SECONDARY_SMALL = """
    QPushButton {
        background-color: #2196F3;
        color: white;
        padding: 5px 10px;
        border-radius: 4px;
    }
    QPushButton:hover { background-color: #1976D2; }
"""

# ============ HEADER STYLES ============

# Page/Tab header style (large)
HEADER_STYLE_LARGE = "font-size: 20px; font-weight: bold;"

# Dialog header style (medium)
HEADER_STYLE = "font-size: 18px; font-weight: bold;"

# Section header style (small)
HEADER_STYLE_SMALL = "font-size: 16px; font-weight: bold;"

# ============ FOOTER/LABEL STYLES ============

# Footer label style
FOOTER_STYLE = "font-size: 13px; color: #555; padding: 5px 10px;"

# Subtitle/info style
INFO_STYLE = "font-size: 14px; color: #666;"

# Error text style
ERROR_STYLE = "color: red;"

# User info bar style
USER_INFO_STYLE = "font-size: 14px; font-weight: bold; color: #333;"

# ============ TEXT INPUT STYLES ============


INPUT_STYLE = """
    QLineEdit {
        padding: 8px 12px;
        border: 1px solid #ccc;
        border-radius: 4px;
        font-size: 14px;
    }
    QLineEdit:focus {
        border-color: #4CAF50;
    }
"""

# ============ TABLE STYLES ============

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

# ============ LIST STYLES ============

LIST_STYLE = """
    QListWidget {
        border: 1px solid #ccc;
        border-radius: 4px;
        font-size: 14px;
    }
    QListWidget::item {
        padding: 10px;
        border-bottom: 1px solid #eee;
    }
    QListWidget::item:selected {
        background-color: #4CAF50;
        color: white;
    }
    QListWidget::item:hover {
        background-color: #e8f5e9;
    }
"""

# Sidebar navigation style
SIDEBAR_STYLE = """
    QListWidget {
        background-color: #f5f5f5;
        border: 1px solid #ddd;
        border-radius: 8px;
        font-size: 14px;
        padding: 3px;
    }
    QListWidget::item {
        color: #333;
        padding: 10px 8px;
        margin: 1px 0;
        border-radius: 6px;
    }
    QListWidget::item:selected {
        background-color: #4CAF50;
        color: white;
    }
    QListWidget::item:hover:!selected {
        background-color: #2196F3;
        color: white;
    }
"""
