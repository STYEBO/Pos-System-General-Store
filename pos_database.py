-- Users table (for authentication and authorization)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'cashier',  -- 'admin' or 'cashier'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    barcode TEXT UNIQUE,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Sales table (header information)
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    user_id INTEGER NOT NULL,
    total_amount REAL NOT NULL,
    amount_paid REAL NOT NULL,
    change_given REAL NOT NULL,
    payment_method TEXT NOT NULL,  -- 'cash' or 'card'
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Sale items table (line items for each sale)
CREATE TABLE IF NOT EXISTS sale_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_products_barcode ON products(barcode);
CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date);
CREATE INDEX IF NOT EXISTS idx_sale_items_sale_id ON sale_items(sale_id);
CREATE INDEX IF NOT EXISTS idx_sale_items_product_id ON sale_items(product_id);

-- Insert default admin user
INSERT OR IGNORE INTO users (username, password, full_name, role) 
VALUES ('admin', 'admin123', 'System Administrator', 'admin');

-- Sample products (optional)
INSERT OR IGNORE INTO products (barcode, name, price, stock) VALUES
('123456789', 'Premium Coffee', 4.99, 100),
('987654321', 'Organic Tea', 3.49, 75),
('456123789', 'Chocolate Bar', 1.99, 200),
('789123456', 'Bottled Water', 0.99, 150),
('321654987', 'Energy Drink', 2.49, 50);

-- Sample customers (optional)
INSERT OR IGNORE INTO customers (name, phone, email, address) VALUES
('John Smith', '555-123-4567', 'john@example.com', '123 Main St'),
('Sarah Johnson', '555-987-6543', 'sarah@example.com', '456 Oak Ave'),
('Mike Williams', '555-456-7890', 'mike@example.com', '789 Pine Rd');
