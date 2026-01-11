# controllers/export_controller.py
"""
Controller for OCR and Export operations.
"""
from PyQt6.QtWidgets import QMessageBox, QFileDialog


class ExportController:
    """Handles OCR scanning and data export."""

    def __init__(self, view, ocr_service, report_service, parent_controller):
        self.view = view
        self.ocr_service = ocr_service
        self.report_service = report_service
        self.parent = parent_controller

    def scan_with_ocr(self):
        """
        Handle the OCR.space button click:
        1. Open file picker
        2. Process image with API
        3. Open Add Dialog with pre-filled data
        """
        # Open file dialog to select image
        file_name, _ = QFileDialog.getOpenFileName(
            self.view,
            "Select Shipping Label Image",
            "",
            "Images (*.png *.xpm *.jpg *.jpeg)"
        )

        if file_name:
            # 1. Extract raw text using OCR.space
            raw_text = self.ocr_service.extract_text(file_name)

            if not raw_text:
                QMessageBox.warning(
                    self.view, "Lỗi", "Không thể đọc văn bản từ hình ảnh."
                )
                return

            # 2. Parse info
            parsed_data = self.ocr_service.parse_order_info(raw_text)

            # 3. Open the dialog with this data
            self.parent.order_ctrl.open_add_order_dialog(extracted_data=parsed_data)

    def export_data(self):
        """
        Handle the Export button click.
        Opens a file dialog to save the Excel file.
        """
        # Open 'Save As' dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self.view,
            "Export Data",
            "Orders_Report.xlsx",  # Default filename
            "Excel Files (*.xlsx)"
        )

        if file_path:
            # Call service to export
            success, message = self.report_service.export_to_excel(file_path)

            if success:
                QMessageBox.information(self.view, "Success", message)
            else:
                QMessageBox.critical(self.view, "Error", message)
