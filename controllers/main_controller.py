# controllers/main_controller.py
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem, QFileDialog, QMenu
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QShortcut, QKeySequence
from ui.main_window import MainWindow
from ui.add_order_dialog import AddOrderDialog
from ui.edit_order_dialog import EditOrderDialog
from ui.order_detail_dialog import OrderDetailDialog
from services.order_service import OrderService
from services.ocrspace_service import OCRSpaceService
from services.report_service import ReportService
from services.action_history import action_history, Action

class MainController:
    def __init__(self, user_data=None, auth_service=None):
        self.user_data = user_data or {}
        self.auth_service = auth_service
        self.is_admin = self.user_data.get('is_admin', False)
        
        # Initialize Views and Services
        self.view = MainWindow(user_data=user_data, auth_service=auth_service)
        self.service = OrderService()
        self.ocr_service = OCRSpaceService()
        self.report_service = ReportService()
        
        # Connect signals
        self.view.btn_add.clicked.connect(self.open_add_order_dialog)
        self.view.btn_refresh.clicked.connect(self.load_orders)
        
        # Connect the OCR.space scan button
        self.view.btn_scan_ai.clicked.connect(self.scan_with_ocr)
        
        # Connect Search (realtime + enter)
        self.view.search_input.returnPressed.connect(self.apply_filters)
        self.view.search_input.textChanged.connect(self.apply_filters)
        
        # Connect Filters
        self.view.filter_status.currentTextChanged.connect(self.apply_filters)
        self.view.filter_time.currentTextChanged.connect(self.apply_filters)
        self.view.filter_province.currentTextChanged.connect(self.apply_filters)
        self.view.btn_clear_filter.clicked.connect(self.clear_filters)
        
        # Connect the Export button (Admin only)
        self.view.btn_export.clicked.connect(self.export_data)
        
        # Hide buttons for Staff users
        if not self.is_admin:
            self.view.btn_export.setVisible(False)

        self.view.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.view.table.customContextMenuRequested.connect(self.show_context_menu)
        self.view.table.itemDoubleClicked.connect(self.on_item_double_clicked)

        # Setup Undo/Redo shortcuts
        self.setup_undo_redo_shortcuts()

        # Load provinces for filter dropdown
        self.load_province_filter()

        # Initial load
        self.load_orders()
        self.view.show()

    def setup_undo_redo_shortcuts(self):
        """Setup Cmd+Z (Undo) and Cmd+Shift+Z (Redo) via Edit menu."""
        from PyQt6.QtGui import QAction
        
        # Create Edit menu
        edit_menu = self.view.menuBar().addMenu("Chỉnh sửa")
        
        # Undo action
        self.undo_action = QAction("↩️ Hoàn tác", self.view)
        self.undo_action.setShortcut("Ctrl+Z")
        self.undo_action.triggered.connect(self.perform_undo)
        edit_menu.addAction(self.undo_action)
        
        # Redo action (Cmd+Shift+Z or Cmd+Y)
        self.redo_action = QAction("↪️ Làm lại", self.view)
        self.redo_action.setShortcut("Ctrl+Y")  # Cmd+Y on Mac
        self.redo_action.triggered.connect(self.perform_redo)
        edit_menu.addAction(self.redo_action)
        
        # Alternative Redo shortcut (Cmd+Shift+Z)
        self.redo_action2 = QAction("↪️ Làm lại (Alt)", self.view)
        self.redo_action2.setShortcut("Ctrl+Shift+Z")
        self.redo_action2.triggered.connect(self.perform_redo)
        self.redo_action2.setVisible(False)  # Hidden from menu
        edit_menu.addAction(self.redo_action2)

    def perform_undo(self):
        """Perform undo action."""
        if not action_history.can_undo():
            self.view.statusBar().showMessage("Không có gì để hoàn tác", 2000)
            return
        
        action = action_history.undo()
        if action:
            success = self._execute_undo(action)
            if success:
                self.view.statusBar().showMessage(f"Đã hoàn tác: {action.action_type} đơn #{action.entity_id}", 3000)
                self.load_orders()
            else:
                self.view.statusBar().showMessage("Không thể hoàn tác", 2000)

    def perform_redo(self):
        """Perform redo action."""
        if not action_history.can_redo():
            self.view.statusBar().showMessage("Không có gì để làm lại", 2000)
            return
        
        action = action_history.redo()
        if action:
            success = self._execute_redo(action)
            if success:
                self.view.statusBar().showMessage(f"Đã làm lại: {action.action_type} đơn #{action.entity_id}", 3000)
                self.load_orders()
            else:
                self.view.statusBar().showMessage("Không thể làm lại", 2000)

    def _execute_undo(self, action: Action) -> bool:
        """Execute the undo operation based on action type."""
        try:
            if action.action_type == 'status_change' and action.entity_type == 'order':
                # Revert to old status
                old_status = action.old_data.get('status') if action.old_data else None
                if old_status:
                    success, _ = self.service.update_order_status(action.entity_id, old_status)
                    return success
            elif action.action_type == 'update' and action.entity_type == 'order':
                # Revert to old data
                if action.old_data:
                    success, _ = self.service.update_order(action.entity_id, action.old_data)
                    return success
            elif action.action_type == 'delete' and action.entity_type == 'order':
                # Restore deleted order - create_order returns 3 values
                if action.old_data:
                    result = self.service.create_order(action.old_data)
                    success = result[0]
                    new_id = result[2] if len(result) > 2 else None
                    if success and new_id:
                        # Update action with new ID for future redo
                        action.entity_id = new_id
                    return success
            elif action.action_type == 'create' and action.entity_type == 'order':
                # Delete the created order
                success, _ = self.service.delete_order(action.entity_id)
                return success
            return False
        except Exception as e:
            print(f"Undo error: {e}")
            return False

    def _execute_redo(self, action: Action) -> bool:
        """Execute the redo operation based on action type."""
        try:
            if action.action_type == 'status_change' and action.entity_type == 'order':
                # Apply new status again
                new_status = action.new_data.get('status') if action.new_data else None
                if new_status:
                    success, _ = self.service.update_order_status(action.entity_id, new_status)
                    return success
            elif action.action_type == 'update' and action.entity_type == 'order':
                # Apply new data again
                if action.new_data:
                    success, _ = self.service.update_order(action.entity_id, action.new_data)
                    return success
            elif action.action_type == 'create' and action.entity_type == 'order':
                # Recreate order
                if action.new_data:
                    result = self.service.create_order(action.new_data)
                    success = result[0]
                    new_id = result[2] if len(result) > 2 else None
                    if success and new_id:
                        # Update action with new ID
                        action.entity_id = new_id
                    return success
            elif action.action_type == 'delete' and action.entity_type == 'order':
                # Delete again
                success, _ = self.service.delete_order(action.entity_id)
                return success
            return False
        except Exception as e:
            print(f"Redo error: {e}")
            return False

    def load_orders(self, orders=None):
        """
        Fetch data, update Table AND update Dashboard.
        If orders is provided, use that list instead of fetching all.
        """
        if orders is None or not isinstance(orders, list):
            orders = self.service.get_all_orders()
            # Clear search input when refreshing
            self.view.search_input.clear()
        
        # 1. Update Table (Tab 1) with new columns
        # Disable sorting while adding rows to prevent data loss
        self.view.table.setSortingEnabled(False)
        self.view.table.setRowCount(0)
        for row_idx, order in enumerate(orders):
            self.view.table.insertRow(row_idx)
            
            # Col 0: Mã đơn
            tracking_item = QTableWidgetItem(order.tracking_code)
            tracking_item.setData(Qt.ItemDataRole.UserRole, order.id)
            tracking_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.view.table.setItem(row_idx, 0, tracking_item)
            
            # Col 1: Trạng thái
            status_item = QTableWidgetItem(order.status)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.view.table.setItem(row_idx, 1, status_item)
            
            # Col 2: Người gửi → Người nhận (Align Left - default)
            sender = order.sender_name or "N/A"
            receiver = order.receiver_name or "N/A"
            self.view.table.setItem(row_idx, 2, QTableWidgetItem(f"{sender} → {receiver}"))
            
            # Col 3: Tuyến đường
            route = order.get_route_summary() if hasattr(order, 'get_route_summary') else "N/A → N/A"
            route_item = QTableWidgetItem(route)
            route_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.view.table.setItem(row_idx, 3, route_item)
            
            # Col 4: Số kiện / Trọng lượng
            package_info = order.get_package_summary() if hasattr(order, 'get_package_summary') else f"1 kiện / {order.weight:.1f} kg"
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

        # Update Quick Stats
        total_count = len(orders) if orders else 0
        shipping_count = sum(1 for o in orders if o.status == "Shipping") if orders else 0
        delivered_count = sum(1 for o in orders if o.status == "Delivered") if orders else 0
        new_count = sum(1 for o in orders if o.status == "New") if orders else 0
        self.view.lbl_quick_stats.setText(
            f"📦 Tổng: {total_count} | 🆕 Mới: {new_count} | 🚚 Đang giao: {shipping_count} | ✅ Đã giao: {delivered_count}"
        )
        
        # Re-enable sorting after adding rows
        self.view.table.setSortingEnabled(True)

        # 2. Update Dashboard Chart (Tab 2)
        self.view.tab_dashboard.update_chart(orders)

    def load_province_filter(self):
        """Load unique provinces into the filter dropdown."""
        provinces = self.service.get_unique_provinces()
        for prov in provinces:
            self.view.filter_province.addItem(prov)

    def apply_filters(self):
        """
        Apply all filters (search + status + time + province).
        """
        search_query = self.view.search_input.text()
        status = self.view.filter_status.currentText()
        time_filter = self.view.filter_time.currentText()
        province = self.view.filter_province.currentText()
        
        # Convert time filter to days
        days = 0
        if time_filter == "Hôm nay":
            days = 1
        elif time_filter == "7 ngày qua":
            days = 7
        elif time_filter == "30 ngày qua":
            days = 30
        
        orders = self.service.filter_orders(
            search_query=search_query,
            status=status,
            days=days,
            province=province
        )
        self.load_orders(orders)

    def clear_filters(self):
        """Reset all filters to default values."""
        self.view.search_input.clear()
        self.view.filter_status.setCurrentIndex(0)
        self.view.filter_time.setCurrentIndex(0)
        self.view.filter_province.setCurrentIndex(0)
        self.load_orders()

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
                self.load_orders()
            else:
                QMessageBox.critical(self.view, "Error", message)

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
                QMessageBox.warning(self.view, "Lỗi", "Không thể đọc văn bản từ hình ảnh.")
                return
                
            # 2. Parse info
            parsed_data = self.ocr_service.parse_order_info(raw_text)
            
            # 3. Open the dialog with this data
            self.open_add_order_dialog(extracted_data=parsed_data)

    def export_data(self):
        """
        Handle the Export button click.
        Opens a file dialog to save the Excel file.
        """
        # Open 'Save As' dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self.view,
            "Export Data",
            "Orders_Report.xlsx", # Default filename
            "Excel Files (*.xlsx)"
        )
        
        if file_path:
            # Call service to export
            success, message = self.report_service.export_to_excel(file_path)
            
            if success:
                QMessageBox.information(self.view, "Success", message)
            else:
                QMessageBox.critical(self.view, "Error", message)

    def show_context_menu(self, pos: QPoint):
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
                action_delete = menu.addAction(f"🗑️ Delete {len(selected_order_ids)} orders (Xoá {len(selected_order_ids)} đơn)")
            else:
                action_delete = menu.addAction("🗑️ Delete (Xoá đơn hàng)")
        
        # Show menu at mouse position and wait for user selection
        action = menu.exec(self.view.table.viewport().mapToGlobal(pos))
        
        # Process selection
        if action:
            # Handle delete action
            if action == action_delete:
                if is_multi_select:
                    self.delete_multiple_orders(selected_order_ids, selected_tracking_codes)
                else:
                    self.delete_order(selected_order_ids[0], selected_tracking_codes[0])
                return
            
            # Handle edit action (single only)
            if action == action_edit:
                self.edit_order(selected_order_ids[0])
                return
            
            # Handle warehouse transfer via dialog
            if action == action_warehouse:
                from ui.warehouse_select_dialog import WarehouseSelectDialog
                from services.warehouse_service import WarehouseService
                dialog = WarehouseSelectDialog(self.view, order_count=len(selected_order_ids))
                if dialog.exec():
                    warehouse_id = dialog.get_selected_warehouse_id()
                    if warehouse_id:
                        ws = WarehouseService()
                        for order_id in selected_order_ids:
                            ws.assign_order_to_warehouse(order_id, warehouse_id)
                        self.load_orders()
                        self.view.statusBar().showMessage(f"Đã chuyển {len(selected_order_ids)} đơn vào kho", 3000)
                return
            
            # Handle status change for all selected
            new_status = ""
            if action == action_new: new_status = "New"
            elif action == action_shipping: new_status = "Shipping"
            elif action == action_done: new_status = "Delivered"
            elif action == action_cancel: new_status = "Cancelled"
            
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
            
            # No need to display a notification popup to avoid annoyance, just reload the table.
            self.load_orders()
            # Update the status bar if desired
            self.view.statusBar().showMessage(message, 3000)
        else:
            QMessageBox.warning(self.view, "Error", message)

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
                
                self.load_orders()
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
            
            self.load_orders()
            self.view.statusBar().showMessage(f"Đã xoá {success_count}/{count} đơn hàng", 3000)

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
                self.load_orders()
            else:
                QMessageBox.critical(self.view, "Lỗi", message)