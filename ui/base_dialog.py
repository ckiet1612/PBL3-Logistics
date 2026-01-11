# ui/base_dialog.py
"""
Base dialog class with common functionality to reduce code duplication.
"""
from PyQt6.QtWidgets import (QDialog, QFormLayout, QHBoxLayout,
                             QLineEdit, QDialogButtonBox, QDoubleSpinBox,
                             QCheckBox, QComboBox, QSpinBox, QTextEdit,
                             QTabWidget, QWidget, QLabel, QPushButton,
                             QCompleter)
from PyQt6.QtCore import Qt
from ui.constants import VIETNAM_PROVINCES, BUTTON_STYLE_PRIMARY, HEADER_STYLE


class BaseDialog(QDialog):
    """Base class for all dialogs with common functionality."""

    def __init__(self, parent=None, title="Dialog", min_width=650, min_height=600):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(min_width, min_height)

        # Initialize attributes (pylint W0201 fix)
        self.buttons = None
        self.btn_save = None
        self.btn_cancel = None
        self.tabs = None

    def setup_tabs(self, layout):
        """Create and add TabWidget to layout."""
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        return self.tabs

    def setup_buttons(self, layout, save_text="Lưu", cancel_text="Huỷ"):
        """Create Save/Cancel button box."""
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.button(QDialogButtonBox.StandardButton.Save).setText(save_text)
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(cancel_text)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        return self.buttons

    def setup_custom_buttons(self, layout, save_text="Lưu", cancel_text="Huỷ"):
        """Create custom button layout (for non-standard dialogs)."""
        btn_layout = QHBoxLayout()

        self.btn_save = QPushButton(save_text)
        self.btn_save.setStyleSheet(BUTTON_STYLE_PRIMARY)
        self.btn_save.clicked.connect(self.accept)

        self.btn_cancel = QPushButton(cancel_text)
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_cancel)
        layout.addRow(btn_layout)
        return btn_layout

    def create_header(self, layout, text, icon=""):
        """Create a styled header label."""
        header = QLabel(f"{icon} {text}" if icon else text)
        header.setStyleSheet(HEADER_STYLE)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        return header

    def set_combo_value(self, combo, value):
        """Set combo box value, adding if not exists."""
        if not value:
            combo.setCurrentIndex(0)
            return

        idx = combo.findText(str(value))
        if idx >= 0:
            combo.setCurrentIndex(idx)
        else:
            combo.setCurrentText(str(value))

    def create_province_combo(self, with_completer=True):
        """Create a province ComboBox with optional completer."""
        combo = QComboBox()
        combo.addItems(VIETNAM_PROVINCES)
        combo.setEditable(True)
        combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        if with_completer:
            completer = QCompleter(VIETNAM_PROVINCES)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)
            combo.setCompleter(completer)

        return combo

    def create_text_input(self, placeholder=""):
        """Create a QLineEdit with optional placeholder."""
        txt = QLineEdit()
        if placeholder:
            txt.setPlaceholderText(placeholder)
        return txt

    def create_text_area(self, placeholder="", max_height=60):
        """Create a QTextEdit with optional placeholder."""
        txt = QTextEdit()
        txt.setMaximumHeight(max_height)
        if placeholder:
            txt.setPlaceholderText(placeholder)
        return txt

    def create_spin_box(self, min_val=0, max_val=100, default=1):
        """Create a QSpinBox with range and default value."""
        spin = QSpinBox()
        spin.setRange(min_val, max_val)
        spin.setValue(default)
        return spin

    def create_double_spin_box(self, min_val=0.0, max_val=1000.0, default=0.0,
                               decimals=1, suffix=""):
        """Create a QDoubleSpinBox with range, default and optional suffix."""
        spin = QDoubleSpinBox()
        spin.setRange(min_val, max_val)
        spin.setValue(default)
        spin.setDecimals(decimals)
        if suffix:
            spin.setSuffix(suffix)
        return spin

    def create_checkbox(self, text="", checked=False):
        """Create a QCheckBox with optional default state."""
        checkbox = QCheckBox(text)
        checkbox.setChecked(checked)
        return checkbox

    def create_combo_with_items(self, items, editable=False):
        """Create a QComboBox with predefined items."""
        combo = QComboBox()
        combo.addItems(items)
        combo.setEditable(editable)
        return combo

    def create_form_tab(self, tab_title, icon=""):
        """Create a tab with a form layout and add to tabs."""
        tab = QWidget()
        form = QFormLayout(tab)
        form.setSpacing(10)

        title = f"{icon} {tab_title}" if icon else tab_title
        if self.tabs:
            self.tabs.addTab(tab, title)

        return tab, form
