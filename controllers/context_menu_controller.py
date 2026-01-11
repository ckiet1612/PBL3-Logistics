# controllers/context_menu_controller.py
"""
Controller for context menu and status change operations.
"""
from PyQt6.QtWidgets import QMessageBox, QMenu
from PyQt6.QtCore import Qt
from services.action_history import action_history, Action


class ContextMenuController:
    """Handles context menu and status changes."""

    def __init__(self, view, service, parent_controller):
        self.view = view
        self.service = service
        self.parent = parent_controller
        self.is_admin = parent_controller.is_admin

    def show_context_menu(self, pos):
        """
        Show right-click menu to change status.
        Supports multi-select for bulk operations.
        """
        # Get selected rows
        selected_rows = self.view.table.selectionModel().selectedRows()
        if not selected_rows:
            return

        # Get order IDs from selected rows
        selected_order_ids = []
        selected_tracking_codes = []
        for index in selected_rows:
            row = index.row()
            order_id = self.view.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            tracking_code = self.view.table.item(row, 0).text()
            if order_id:
                selected_order_ids.append(order_id)
                selected_tracking_codes.append(tracking_code)

        is_multi_select = len(selected_order_ids) > 1

        # Create menu
        menu = QMenu()

        # Create status change actions
        action_new = menu.addAction("Set: New (Mới tạo)")
        action_processing = menu.addAction("Set: Processing (Đang xử lý)")
        action_shipping = menu.addAction("Set: Shipping (Đang giao)")
        action_done = menu.addAction("Set: Delivered (Đã giao)")
        action_cancel = menu.addAction("Set: Cancelled (Đã hủy)")

        # Add separator and edit action (only for single selection)
        menu.addSeparator()
        action_edit = None
        if not is_multi_select:
            action_edit = menu.addAction("✏️ Edit (Sửa đơn hàng)")

        # Warehouse transfer action (opens dialog)
        action_warehouse = menu.addAction("🏭 Chuyển kho...")

        # Add delete action (Admin only)
        action_delete = None
        if self.is_admin:
            if is_multi_select:
                action_delete = menu.addAction(
                    f"🗑️ Delete {len(selected_order_ids)} orders (Xoá {len(selected_order_ids)} đơn)"
                )
            else:
                action_delete = menu.addAction("🗑️ Delete (Xoá đơn hàng)")

        # Show menu at mouse position and wait for user selection
        action = menu.exec(self.view.table.viewport().mapToGlobal(pos))

        # Process selection
        if action:
            # Handle delete action
            if action == action_delete:
                if is_multi_select:
                    self.parent.order_ctrl.delete_multiple_orders(
                        selected_order_ids, selected_tracking_codes
                    )
                else:
                    self.parent.order_ctrl.delete_order(
                        selected_order_ids[0], selected_tracking_codes[0]
                    )
                return

            # Handle edit action (single only)
            if action == action_edit:
                self.parent.order_ctrl.edit_order(selected_order_ids[0])
                return

            # Handle warehouse transfer via dialog
            if action == action_warehouse:
                from ui.warehouse_select_dialog import WarehouseSelectDialog
                from services.warehouse_service import WarehouseService
                dialog = WarehouseSelectDialog(
                    self.view, order_count=len(selected_order_ids)
                )
                if dialog.exec():
                    warehouse_id = dialog.get_selected_warehouse_id()
                    if warehouse_id:
                        ws = WarehouseService()
                        for order_id in selected_order_ids:
                            ws.assign_order_to_warehouse(order_id, warehouse_id)
                        self.parent.load_orders()
                        self.view.statusBar().showMessage(
                            f"Đã chuyển {len(selected_order_ids)} đơn vào kho", 3000
                        )
                return

            # Handle status change for all selected
            new_status = ""
            if action == action_new:
                new_status = "New"
            elif action == action_processing:
                new_status = "Processing"
            elif action == action_shipping:
                new_status = "Shipping"
            elif action == action_done:
                new_status = "Delivered"
            elif action == action_cancel:
                new_status = "Cancelled"

            # Apply status to all selected orders
            if new_status:
                for order_id in selected_order_ids:
                    self.change_status(order_id, new_status)

    def change_status(self, order_id, new_status):
        """Call service to update status and refresh UI."""
        # Get current status before update for undo
        order = self.service.get_order_by_id(order_id)
        if order:
            old_status = order.get('status') if isinstance(order, dict) else order.status
        else:
            old_status = None

        success, message = self.service.update_order_status(order_id, new_status)

        if success:
            # Record action for undo
            if old_status:
                action = Action(
                    action_type='status_change',
                    entity_type='order',
                    entity_id=order_id,
                    old_data={'status': old_status},
                    new_data={'status': new_status}
                )
                action_history.record_action(action)

            # Smart filter: check if status change affects current filter
            self.parent.filter_ctrl.refresh_with_smart_filter(
                {'status': old_status},
                {'status': new_status}
            )
            # Update the status bar
            self.view.statusBar().showMessage(message, 3000)
        else:
            QMessageBox.warning(self.view, "Error", message)
