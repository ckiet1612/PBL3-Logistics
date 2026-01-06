# services/transport_service.py

class TransportService:
    def __init__(self):
        # Base rates configuration
        self.base_price_under_1kg = 30000.0
        self.base_price_1_to_5kg = 45000.0
        self.surcharge_per_kg = 5000.0

    def calculate_shipping_fee(self, weight_kg):
        """
        Calculate shipping fee based on weight.

        Pricing Rules:
        - Weight <= 1kg: 30,000 VND
        - 1kg < Weight <= 5kg: 45,000 VND
        - Weight > 5kg: 45,000 + (Weight - 5) * 5,000 VND

        :param weight_kg: Weight in Kilograms (float)
        :return: Calculated cost in VND (float)
        """
        if weight_kg <= 0:
            return 0.0

        if weight_kg <= 1.0:
            return self.base_price_under_1kg

        elif weight_kg <= 5.0:
            return self.base_price_1_to_5kg

        else:
            # Calculate extra weight
            extra_weight = weight_kg - 5.0
            # Round up logic: 5.1kg counts as 6kg excess?
            # For simplicity, we just multiply exactly.
            total_fee = self.base_price_1_to_5kg + (extra_weight * self.surcharge_per_kg)
            return total_fee
