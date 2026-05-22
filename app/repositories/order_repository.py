# Import Oracle DB driver, JSON library, and database configuration
import json
import oracledb
from config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_SERVICE


class OrderRepository:

    def _get_connection(self):
        dsn = f"{DB_HOST}:{DB_PORT}/{DB_SERVICE}"
        return oracledb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=dsn
        )

    def get_all_orders(self):
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT order_id, customer_name, status, category, details, total_amount
                FROM orders
                ORDER BY created_at DESC, order_id DESC
            """)

            rows = cursor.fetchall()
            orders = []

            for row in rows:
                order_id, customer_name, status, category, details, total_amount = row
                saved_total = float(total_amount) if total_amount is not None else 0.0

                item_cursor = conn.cursor()
                try:
                    item_cursor.execute("""
                        SELECT item_name, price
                        FROM order_items
                        WHERE order_id = :order_id
                        ORDER BY item_id
                    """, {"order_id": order_id})

                    items = []
                    items_total = 0.0

                    for name, price in item_cursor.fetchall():
                        price_val = float(price) if price is not None else 0.0
                        items.append({
                            "item_name": name or "",
                            "price": price_val
                        })
                        items_total += price_val
                finally:
                    item_cursor.close()

                main_price = round(saved_total - items_total, 2)
                if main_price < 0:
                    main_price = 0.0

                orders.append({
                    "order_id": order_id,
                    "customer_name": customer_name,
                    "status": status,
                    "category": category,
                    "details": details or "",
                    "main_price": main_price,
                    "total_amount": saved_total,
                    "items": items
                })

            return orders

        finally:
            cursor.close()
            conn.close()

    def insert_order(self, order):
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO orders (
                    order_id, customer_name, status, category, details, total_amount, created_at
                ) VALUES (
                    :order_id, :customer_name, :status, :category, :details, :total_amount, SYSDATE
                )
            """, {
                "order_id": order["order_id"],
                "customer_name": order["customer_name"],
                "status": order["status"],
                "category": order["category"],
                "details": order["details"],
                "total_amount": order["total_amount"]
            })

            for item in order.get("items", []):
                cursor.execute("""
                    INSERT INTO order_items (order_id, item_name, price)
                    VALUES (:order_id, :item_name, :price)
                """, {
                    "order_id": order["order_id"],
                    "item_name": item["item_name"],
                    "price": item["price"]
                })

            conn.commit()

        except oracledb.IntegrityError as e:
            conn.rollback()
            error_obj = e.args[0]
            if hasattr(error_obj, "code") and error_obj.code == 1:
                raise ValueError("Do not enter duplicate Order ID. This Order ID already exists.")
            raise ValueError("Database integrity error occurred.")

        except oracledb.DatabaseError:
            conn.rollback()
            raise ValueError("Unable to save order in database.")

        finally:
            cursor.close()
            conn.close()

    def update_order(self, order):
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE orders
                SET customer_name = :customer_name,
                    status = :status,
                    category = :category,
                    details = :details,
                    total_amount = :total_amount
                WHERE order_id = :order_id
            """, {
                "order_id": order["order_id"],
                "customer_name": order["customer_name"],
                "status": order["status"],
                "category": order["category"],
                "details": order["details"],
                "total_amount": order["total_amount"]
            })

            cursor.execute("""
                DELETE FROM order_items
                WHERE order_id = :order_id
            """, {"order_id": order["order_id"]})

            for item in order.get("items", []):
                cursor.execute("""
                    INSERT INTO order_items (order_id, item_name, price)
                    VALUES (:order_id, :item_name, :price)
                """, {
                    "order_id": order["order_id"],
                    "item_name": item["item_name"],
                    "price": item["price"]
                })

            conn.commit()

        except oracledb.DatabaseError:
            conn.rollback()
            raise ValueError("Unable to update order in database.")

        finally:
            cursor.close()
            conn.close()

    # Save full order JSON in OUTDOOR_ORDERS table
    # If the order already exists there, update it; otherwise insert a new row
    def save_outdoor_order(self, order):
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            order_json = json.dumps(order).encode("utf-8")

            cursor.execute("""
                SELECT order_id
                FROM outdoor_orders
                WHERE order_no = :order_no
            """, {
                "order_no": order["order_id"]
            })
            existing_row = cursor.fetchone()

            if existing_row:
                cursor.execute("""
                    UPDATE outdoor_orders
                    SET customer_info = :customer_info,
                        order_data = :order_data,
                        created_at = SYSDATE
                    WHERE order_no = :order_no
                """, {
                    "order_no": order["order_id"],
                    "customer_info": order["customer_name"],
                    "order_data": order_json
                })
            else:
                cursor.execute("""
                    INSERT INTO outdoor_orders (
                        order_id, order_no, customer_info, order_data, created_at
                    ) VALUES (
                        outdoor_orders_seq.NEXTVAL,
                        :order_no,
                        :customer_info,
                        :order_data,
                        SYSDATE
                    )
                """, {
                    "order_no": order["order_id"],
                    "customer_info": order["customer_name"],
                    "order_data": order_json
                })

            conn.commit()

        except oracledb.DatabaseError as e:
            conn.rollback()
            print("OUTDOOR_ORDERS save failed:", e)
            raise ValueError("Failed to save JSON in outdoor_orders.")

        finally:
            cursor.close()
            conn.close()

    # Optional: delete JSON copy when deleting order
    def delete_outdoor_order(self, order_id):
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                DELETE FROM outdoor_orders
                WHERE order_no = :order_no
            """, {"order_no": order_id})

            conn.commit()

        except oracledb.DatabaseError as e:
            conn.rollback()
            print("OUTDOOR_ORDERS delete failed:", e)
            raise ValueError("Unable to delete JSON order from outdoor_orders.")

        finally:
            cursor.close()
            conn.close()

    def delete_order(self, order_id):
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                DELETE FROM order_items
                WHERE order_id = :order_id
            """, {"order_id": order_id})

            cursor.execute("""
                DELETE FROM orders
                WHERE order_id = :order_id
            """, {"order_id": order_id})

            conn.commit()

        except oracledb.DatabaseError:
            conn.rollback()
            raise ValueError("Unable to delete order.")

        finally:
            cursor.close()
            conn.close()