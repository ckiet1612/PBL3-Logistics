# controllers/filter_controller.py
"""
Controller for Search and Filter operations.
"""
from ui.constants import VIETNAM_PROVINCES


class FilterController:
    """Handles search, filtering, and smart filter logic."""

    def __init__(self, view, service, parent_controller):
        self.view = view
        self.service = service
        self.parent = parent_controller

    def load_province_filter(self):
        """Load unique provinces into the filter dropdown."""
        # Get provinces from existing orders
        provinces = self.service.get_unique_provinces()

        # If no provinces from orders, use default list
        if not provinces:
            provinces = [p for p in VIETNAM_PROVINCES if p]  # Filter out empty string

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
        self.parent.load_orders(orders)

    def clear_filters(self):
        """Reset all filters to default values."""
        self.view.search_input.clear()
        self.view.filter_status.setCurrentIndex(0)
        self.view.filter_time.setCurrentIndex(0)
        self.view.filter_province.setCurrentIndex(0)
        self.parent.load_orders()

    def refresh_with_smart_filter(self, old_data, new_data):
        """
        Refresh orders with smart filter logic:
        - Clear filter if edited field matches a filtered field
        - Keep filter if edited field doesn't match filtered fields
        """
        # Get current filter values
        filter_status = self.view.filter_status.currentText()
        filter_province = self.view.filter_province.currentText()
        search_query = self.view.search_input.text().strip()

        should_clear_filter = False

        # Check if status filter is active and status was changed
        if filter_status != "Tất cả trạng thái":
            old_status = old_data.get('status', '')
            new_status = new_data.get('status', '')
            if old_status != new_status:
                should_clear_filter = True

        # Check if province filter is active and province was changed
        if filter_province != "Tất cả tỉnh thành":
            old_sender_prov = old_data.get('sender_province', '')
            old_receiver_prov = old_data.get('receiver_province', '')
            new_sender_prov = new_data.get('sender_province', '')
            new_receiver_prov = new_data.get('receiver_province', '')

            if old_sender_prov != new_sender_prov or old_receiver_prov != new_receiver_prov:
                should_clear_filter = True

        # Check if search query is active and relevant fields changed
        if search_query:
            search_fields = ['tracking_code', 'sender_name', 'receiver_name',
                           'sender_phone', 'receiver_phone']
            for field in search_fields:
                if old_data.get(field, '') != new_data.get(field, ''):
                    should_clear_filter = True
                    break

        # Apply appropriate refresh
        if should_clear_filter:
            self.clear_filters()
        else:
            self.apply_filters()
