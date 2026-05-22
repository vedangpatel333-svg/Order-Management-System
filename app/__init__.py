from flask import Flask

def create_app():
    app = Flask(__name__)

    from app.controllers.order_controller import order_bp
    app.register_blueprint(order_bp)

    return app