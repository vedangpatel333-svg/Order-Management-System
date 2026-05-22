import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(BASE_DIR, "data", "orders.json")

DB_USER = "hr"
DB_PASSWORD = "hr"
DB_HOST = "localhost"
DB_PORT = 1521
DB_SERVICE = "FREEPDB1"