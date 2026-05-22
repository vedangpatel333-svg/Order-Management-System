# Import repository and model
from app.repositories.order_repository import OrderRepository
from app.models.order import Order


# Service layer handles form processing and business logic
class OrderService:
    def __init__(self):
        # Create repository instance
        self.repo = OrderRepository()

    # Get all orders from repository
    def get_orders(self):
        return self.repo.get_all_orders()

    # Convert string price safely to float
    def _parse_price(self, value, field_name):
        value = (value or "").strip()

        if not value:
            return 0.0

        try:
            return float(value)
        except ValueError:
            raise ValueError(f"Invalid value for {field_name}.")

    # Build complete order data from submitted form
    def _build_order_data(self, form_data):
        item_names = form_data.getlist("item_name[]")
        item_prices = form_data.getlist("item_price[]")
        main_price_raw = form_data.get("main_price", "0").strip()

        order_id = form_data.get("order_id", "").strip()
        customer_name = form_data.get("customer_name", "").strip()
        status = form_data.get("status", "").strip()
        category = form_data.get("category", "").strip()
        details = form_data.get("details", "").strip()

        # Validate required fields
        if not order_id:
            raise ValueError("Order ID is required.")
        if not customer_name:
            raise ValueError("Customer name is required.")
        if not status:
            raise ValueError("Status is required.")
        if not category:
            raise ValueError("Category is required.")

        items = []
        main_price = self._parse_price(main_price_raw, "main price")
        total_amount = main_price

        # Build item list and calculate total
        for name, price in zip(item_names, item_prices):
            name = name.strip()
            price = price.strip()

            if name or price:
                price_value = self._parse_price(price, "item price")
                items.append({
                    "item_name": name,
                    "price": price_value
                })
                total_amount += price_value

        # Create Order model object
        order = Order(
            order_id=order_id,
            customer_name=customer_name,
            status=status,
            category=category,
            details=details,
            items=items,
            main_price=main_price
        )

        # Convert object to dictionary
        order_data = order.to_dict()
        order_data["total_amount"] = round(total_amount, 2)

        return order_data

    # Create new order
    def create_order(self, form_data):
        order_data = self._build_order_data(form_data)

        # Save main order data
        self.repo.insert_order(order_data)

        # Save JSON copy in OUTDOOR_ORDERS
        # If this fails, do not break the main order save
        try:
            self.repo.save_outdoor_order(order_data)
        except Exception as e:
            print("JSON save skipped:", e)

        return order_data

    # Update existing order
    def update_order(self, form_data):
        order_data = self._build_order_data(form_data)

        # Update main order data
        self.repo.update_order(order_data)

        # Update or insert JSON copy
        # If this fails, do not break the main order update
        try:
            self.repo.save_outdoor_order(order_data)
        except Exception as e:
            print("JSON update skipped:", e)

        return order_data

    # Delete order
    def delete_order(self, order_id):
        # Delete main order data
        self.repo.delete_order(order_id)

        # Delete JSON copy if possible
        try:
            self.repo.delete_outdoor_order(order_id)
        except Exception as e:
            print("JSON delete skipped:", e)