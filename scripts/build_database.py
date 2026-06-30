
import os
import random
import sqlite3
from datetime import datetime, timedelta

random.seed(42)

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DB_PATH = os.path.join(_BASE_DIR, "data", "database.db")
_SCHEMA_PATH = os.path.join(_BASE_DIR, "data", "schema.sql")

STORES = [
    (1, "Plaisio Athens Center", "Athens", "Attica"),
    (2, "Plaisio Thessaloniki", "Thessaloniki", "Central Macedonia"),
    (3, "Plaisio Patras", "Patras", "Western Greece"),
    (4, "Plaisio Heraklion", "Heraklion", "Crete"),
    (5, "Plaisio Larissa", "Larissa", "Thessaly"),
]

PRODUCT_TEMPLATES = [
    ("Laptops", "UltraBook 14", 749.0),
    ("Laptops", "ProBook 15 Gaming", 1299.0),
    ("Laptops", "ChromeLite 11", 399.0),
    ("Smartphones", "Phone X12", 599.0),
    ("Smartphones", "Phone Lite 5G", 299.0),
    ("Smartphones", "Phone Max Pro", 999.0),
    ("TVs", "Smart TV 55\" 4K", 549.0),
    ("TVs", "Smart TV 65\" OLED", 1199.0),
    ("Appliances", "Washing Machine 8kg", 389.0),
    ("Appliances", "Fridge No-Frost 300L", 549.0),
    ("Appliances", "Vacuum Robot V3", 249.0),
    ("Accessories", "Wireless Mouse", 19.9),
    ("Accessories", "Mechanical Keyboard", 59.9),
    ("Accessories", "Bluetooth Headphones", 79.9),
    ("Accessories", "Power Bank 20000mAh", 34.9),
]


def build():
    os.makedirs(os.path.dirname(_DB_PATH), exist_ok=True)
    if os.path.exists(_DB_PATH):
        os.remove(_DB_PATH)

    conn = sqlite3.connect(_DB_PATH)
    with open(_SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    conn.executemany(
        "INSERT INTO stores (store_id, store_name, city, region) VALUES (?, ?, ?, ?)",
        STORES,
    )

    products = []
    product_id = 1
    for store_id, *_ in STORES:
        for category, name, base_price in PRODUCT_TEMPLATES:
            price = round(base_price * random.uniform(0.95, 1.08), 2)
            products.append((product_id, f"{name}", category, price, store_id))
            product_id += 1

    conn.executemany(
        "INSERT INTO products (product_id, name, category, price, store_id) VALUES (?, ?, ?, ?, ?)",
        products,
    )

    sales = []
    sale_id = 1
    start_date = datetime(2025, 1, 1)
    for _ in range(220):
        product = random.choice(products)
        product_id_pick, _, _, price, _ = product
        days_offset = random.randint(0, 540)  # spans into 2026
        sale_date = (start_date + timedelta(days=days_offset)).strftime("%Y-%m-%d")
        quantity = random.randint(1, 4)
        total_amount = round(price * quantity, 2)
        sales.append((sale_id, product_id_pick, sale_date, quantity, total_amount))
        sale_id += 1

    conn.executemany(
        "INSERT INTO sales (sale_id, product_id, sale_date, quantity, total_amount) "
        "VALUES (?, ?, ?, ?, ?)",
        sales,
    )

    conn.commit()
    conn.close()
    print(f"Built {_DB_PATH}: {len(STORES)} stores, {len(products)} products, {len(sales)} sales.")


if __name__ == "__main__":
    build()
