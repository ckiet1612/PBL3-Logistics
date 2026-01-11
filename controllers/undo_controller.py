# controllers/undo_controller.py
"""
Controller for Undo/Redo operations.
"""
from PyQt6.QtGui import QAction
from services.action_history import action_history, Action


class UndoController:
    """Handles undo/redo functionality."""

    def __init__(self, view, service, parent_controller):
        self.view = view
        self.service = service
        self.parent = parent_controller
        self.undo_action = None
        self.redo_action = None

    def setup_undo_redo_shortcuts(self):
        """Setup Cmd+Z (Undo) and Cmd+Shift+Z (Redo) via Edit menu."""
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
                self.view.statusBar().showMessage(
                    f"Đã hoàn tác: {action.action_type} đơn #{action.entity_id}", 3000
                )
                self.parent.load_orders()
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
                self.view.statusBar().showMessage(
                    f"Đã làm lại: {action.action_type} đơn #{action.entity_id}", 3000
                )
                self.parent.load_orders()
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
