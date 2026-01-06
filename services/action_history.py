# services/action_history.py
"""
Action History Manager for Undo/Redo functionality.
Tracks changes to orders and allows reversing them.
"""
from collections import deque
from dataclasses import dataclass
from typing import Any, Optional
from datetime import datetime


@dataclass
class Action:
    """Represents an undoable action."""
    action_type: str  # 'create', 'update', 'delete', 'status_change'
    entity_type: str  # 'order', 'warehouse', 'route'
    entity_id: int
    old_data: Optional[dict]  # Data before action (for undo)
    new_data: Optional[dict]  # Data after action (for redo)
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class ActionHistoryManager:
    """Manages undo/redo history."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, max_history: int = 50):
        if self._initialized:
            return
        self._initialized = True
        self.max_history = max_history
        self.undo_stack = deque(maxlen=max_history)
        self.redo_stack = deque(maxlen=max_history)

    def record_action(self, action: Action):
        """Record a new action, clearing redo stack."""
        self.undo_stack.append(action)
        self.redo_stack.clear()  # Clear redo when new action is performed

    def can_undo(self) -> bool:
        return len(self.undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self.redo_stack) > 0

    def undo(self) -> Optional[Action]:
        """Get the last action to undo."""
        if self.can_undo():
            action = self.undo_stack.pop()
            self.redo_stack.append(action)
            return action
        return None

    def redo(self) -> Optional[Action]:
        """Get the last undone action to redo."""
        if self.can_redo():
            action = self.redo_stack.pop()
            self.undo_stack.append(action)
            return action
        return None

    def clear(self):
        """Clear all history."""
        self.undo_stack.clear()
        self.redo_stack.clear()

    def get_undo_description(self) -> str:
        """Get description of action that would be undone."""
        if self.can_undo():
            action = self.undo_stack[-1]
            return self._get_action_description(action, "Hoàn tác")
        return "Không có gì để hoàn tác"

    def get_redo_description(self) -> str:
        """Get description of action that would be redone."""
        if self.can_redo():
            action = self.redo_stack[-1]
            return self._get_action_description(action, "Làm lại")
        return "Không có gì để làm lại"

    def _get_action_description(self, action: Action, prefix: str) -> str:
        """Generate human-readable action description."""
        action_names = {
            'create': 'tạo',
            'update': 'cập nhật',
            'delete': 'xóa',
            'status_change': 'đổi trạng thái'
        }
        entity_names = {
            'order': 'đơn hàng',
            'warehouse': 'kho',
            'route': 'tuyến đường'
        }
        action_name = action_names.get(action.action_type, action.action_type)
        entity_name = entity_names.get(action.entity_type, action.entity_type)
        return f"{prefix} {action_name} {entity_name} #{action.entity_id}"


# Global instance
action_history = ActionHistoryManager()
