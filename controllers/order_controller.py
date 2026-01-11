# controllers/order_controller.py
"""
Controller for Order CRUD operations.
"""
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import Qt
from ui.add_order_dialog import AddOrderDialog
from ui.edit_order_dialog import EditOrderDialog
from ui.order_detail_dialog import OrderDetailDialog
from services.order_service import OrderService
from services.action_history import action_history, Action


class OrderController:
    """Handles order creation, editing, deletion and viewing."""

    def __init__(self, view, service, parent_controller):
        self.view = view
        self.service = service
        self.parent = parent_controller

    def open_add_order_dialog(self, extracted_data=None):
        """
        Open the dialog. If extracted_data is provided, fill the form.
        """
        dialog = AddOrderDialog(self.view)

        # If we have data from OCR.space, auto-fill it
        if extracted_data:
            dialog.fill_data(extracted_data)

        if dialog.exec():
            data = dialog.get_data()
            if not data["tracking_code"]:
                QMessageBox.warning(self.view, "Warning", "Tracking Code is required!")
                return

            result = self.service.create_order(data)
            success = result[0]
            message = result[1]
            order_id = result[2] if len(result) > 2 else None

            if success and order_id:
                # Record action for undo
                data['id'] = order_id  # Store the ID for undo
                action = Action(
                    action_type='create',
                    entity_type='order',
                    entity_id=order_id,
                    old_data=None,
                    new_data=data
                )
                action_history.record_action(action)

                QMessageBox.information(self.view, "Success", message)
                self.parent.load_orders()
            else:
                QMessageBox.critical(self.view, "Error", message)

    def view_order_detail(self, order_id):
        """Open dialog to view full order details."""
        order_data = self.service.get_order_by_id(order_id)
        if order_data:
            dialog = OrderDetailDialog(order_data, self.view)
            dialog.exec()

    def on_item_double_clicked(self, item):
        """Handle double click on a row to view details."""
        row = item.row()
        # Get order_id from column 0 user data
        order_id = self.view.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        if order_id:
            self.view_order_detail(order_id)

    def edit_order(self, order_id):
        """Open dialog to edit order and save changes."""
        # Get current order data (for undo)
        order = self.service.get_order_by_id(order_id)

        if not order:
            QMessageBox.warning(self.view, "Lỗi", "Không tìm thấy đơn hàng")
            return

        # Store old data for undo
        old_data = self.service.order_to_dict(order)

        # Open edit dialog
        dialog = EditOrderDialog(order, self.view)

        if dialog.exec():
            new_data = dialog.get_data()

            if not new_data["tracking_code"]:
                QMessageBox.warning(self.view, "Lỗi", "Mã vận đơn không được để trống!")
                return

            success, message = self.service.update_order(order_id, new_data)

            if success:
                # Record action for undo
                action = Action(
                    action_type='update',
                    entity_type='order',
                    entity_id=order_id,
                    old_data=old_data,
                    new_data=new_data
                )
                action_history.record_action(action)

                QMessageBox.information(self.view, "Thành công", message)

                # Smart filter: check if edited fields affect current filters
                self.parent._refresh_with_smart_filter(old_data, new_data)
            else:
                QMessageBox.critical(self.view, "Lỗi", message)

    def delete_order(self, order_id, tracking_code):
        """Show confirmation and delete order if confirmed."""
        # Get order data before deletion (for undo)
        order = self.service.get_order_by_id(order_id)
        old_data = self.service.order_to_dict(order) if order else None

        # Ask for confirmation
        reply = QMessageBox.question(
            self.view,
            "Xác nhận xoá",
            f"Bạn có chắc chắn muốn xoá đơn hàng {tracking_code}?\n\nBạn có thể hoàn tác bằng ⌘+Z.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.service.delete_order(order_id)

            if success:
                # Record action for undo
                if old_data:
                    action = Action(
                        action_type='delete',
                        entity_type='order',
                        entity_id=order_id,
                        old_data=old_data,
                        new_data=None
                    )
                    action_history.record_action(action)

                self.parent.load_orders()
                self.view.statusBar().showMessage(message, 3000)
            else:
                QMessageBox.warning(self.view, "Error", message)

    def delete_multiple_orders(self, order_ids, tracking_codes):
        """Show confirmation and delete multiple orders if confirmed."""
        count = len(order_ids)
        codes_preview = ", ".join(tracking_codes[:3])
        if count > 3:
            codes_preview += f"... và {count - 3} đơn khác"

        reply = QMessageBox.question(
            self.view,
            "Xác nhận xoá nhiều đơn",
            f"Bạn có chắc chắn muốn xoá {count} đơn hàng?\n\n{codes_preview}\n\nHành động này không thể hoàn tác!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            success_count = 0
            for order_id in order_ids:
                success, _ = self.service.delete_order(order_id)
                if success:
                    success_count += 1

            self.parent.load_orders()
            self.view.statusBar().showMessage(f"Đã xoá {success_count}/{count} đơn hàng", 3000)
