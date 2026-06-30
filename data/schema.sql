CREATE TABLE IF NOT EXISTS stores (
    store_id INTEGER PRIMARY KEY,
    store_name TEXT NOT NULL,
    city TEXT NOT NULL,
    region TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    store_id INTEGER NOT NULL,
    FOREIGN KEY (store_id) REFERENCES stores (store_id)
);

CREATE TABLE IF NOT EXISTS sales (
    sale_id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,
    sale_date TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    total_amount REAL NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products (product_id)
);
