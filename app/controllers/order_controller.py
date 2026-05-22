# Import necessary Flask components and the service layer
from flask import Blueprint, render_template, request, redirect, url_for
from app.services.order_service import OrderService

# Create a Blueprint for order-related routes
order_bp = Blueprint("order", __name__)

# Initialize the service that handles business logic for orders
service = OrderService()


# Route for the home/dashboard page
@order_bp.route("/")
def home():
    # Fetch all orders from the service
    orders = service.get_orders()

    # Render the dashboard template with orders and no error message
    return render_template("dashboard.html", orders=orders, error=None)


# Route to handle creating or updating an order (POST request only)
@order_bp.route("/save_order", methods=["POST"])
def save_order():
    try:
        # Determine whether the form is for creating or updating an order
        form_mode = request.form.get("form_mode", "create")

        # If updating an existing order
        if form_mode == "update":
            service.update_order(request.form)
        else:
            # Otherwise, create a new order
            service.create_order(request.form)

        # Redirect back to the home/dashboard page after success
        return redirect(url_for("order.home"))

    except ValueError as e:
        # Handle validation or expected errors (e.g., bad input)
        orders = service.get_orders()
        return render_template("dashboard.html", orders=orders, error=str(e))

    except Exception:
        # Handle unexpected errors
        orders = service.get_orders()
        return render_template(
            "dashboard.html",
            orders=orders,
            error="Something went wrong while saving the order."
        )


# Route to delete an order by ID (POST request only)
@order_bp.route("/delete_order/<order_id>", methods=["POST"])
def delete_order(order_id):
    try:
        # Call service to delete the order
        service.delete_order(order_id)

        # Return HTTP 204 (No Content) on success
        return "", 204
    except Exception:
        # Return error message with HTTP 500 if deletion fails
        return "Delete failed", 500