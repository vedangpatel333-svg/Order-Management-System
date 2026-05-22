# Order model class representing a single order entity
class Order:
    def __init__(self, order_id, customer_name, status, category, details, items=None, main_price=0.0):
        # Unique identifier for the order
        self.order_id = order_id

        # Name of the customer who placed the order
        self.customer_name = customer_name

        # Current status of the order (e.g., pending, completed)
        self.status = status

        # Category/type of the order
        self.category = category

        # Additional details or description of the order
        self.details = details

        # List of items included in the order (defaults to empty list if None)
        self.items = items if items else []

        # Main price of the order, safely converted to float
        self.main_price = float(main_price) if main_price else 0.0

    # Convert the Order object into a dictionary (useful for JSON responses or templates)
    def to_dict(self):
        return {
            "order_id": self.order_id,
            "customer_name": self.customer_name,
            "status": self.status,
            "category": self.category,
            "details": self.details,
            "items": self.items,
            "main_price": self.main_price
        }