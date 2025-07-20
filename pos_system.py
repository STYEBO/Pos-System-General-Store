import sqlite3
import os
from datetime import datetime
import getpass
import time
import sys

# Database connection
def get_db_connection():
    try:
        conn = sqlite3.connect('pos_database.db')
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        sys.exit(1)

# Initialize database
def init_db():
    if not os.path.exists('pos_database.db'):
        conn = sqlite3.connect('pos_database.db')
        # Create tables
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'cashier',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create other tables
        conn.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT UNIQUE,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                stock INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                user_id INTEGER NOT NULL,
                total_amount REAL NOT NULL,
                amount_paid REAL NOT NULL,
                change_given REAL NOT NULL,
                payment_method TEXT NOT NULL,
                sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                FOREIGN KEY (sale_id) REFERENCES sales(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        ''')
        
        # Insert default admin user
        conn.execute('''
            INSERT INTO users (username, password, full_name, role) 
            VALUES (?, ?, ?, ?)
        ''', ('admin', 'admin123', 'System Administrator', 'admin'))
        conn.commit()
        conn.close()
        print("Database initialized successfully.")

# Clear screen function
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Login system
def login():
    clear_screen()
    print("╔════════════════════════════════════════╗")
    print("║           POS SYSTEM LOGIN            ║")
    print("╚════════════════════════════════════════╝")
    
    while True:
        username = input("Username: ")
        password = getpass.getpass("Password: ")
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and user['password'] == password:
            return user
        else:
            print("Invalid username or password. Try again.")

# Main menu
def main_menu(user):
    while True:
        clear_screen()
        print("╔════════════════════════════════════════╗")
        print("║       GENERAL STORE POS SYSTEM        ║")
        print("╚════════════════════════════════════════╝")
        print(f"\nLogged in as: {user['full_name']} ({user['role']})")
        print("\n1. Product Management")
        print("2. Process Sale")
        print("3. Customer Management")
        print("4. Sale History")
        print("5. Reports")
        if user['role'] == 'admin':
            print("6. System Settings")
            print("7. Exit")
            choices = range(1, 8)
        else:
            print("6. Exit")
            choices = range(1, 7)
        
        try:
            choice = int(input("\nEnter your choice: "))
            if choice not in choices:
                raise ValueError
        except ValueError:
            input("Invalid choice. Press Enter to try again...")
            continue
        
        if choice == 1:
            product_management()
        elif choice == 2:
            process_sale(user)
        elif choice == 3:
            customer_management()
        elif choice == 4:
            sale_history()
        elif choice == 5:
            reports()
        elif choice == 6 and user['role'] == 'admin':
            system_settings()
        elif (choice == 6 and user['role'] != 'admin') or (choice == 7 and user['role'] == 'admin'):
            print("Exiting system...")
            time.sleep(1)
            sys.exit()

# Product Management
def product_management():
    while True:
        clear_screen()
        print("╔════════════════════════════════════════╗")
        print("║          PRODUCT MANAGEMENT          ║")
        print("╚════════════════════════════════════════╝")
        print("\n1. Add Product with barcode")
        print("2. View Products")
        print("3. Update Product")
        print("4. Delete Product")
        print("5. Back to Main Menu")
        
        try:
            choice = int(input("\nEnter your choice (1-5): "))
            if choice not in range(1, 6):
                raise ValueError
        except ValueError:
            input("Invalid choice. Press Enter to try again...")
            continue
        
        if choice == 1:
            add_product()
        elif choice == 2:
            view_products()
        elif choice == 3:
            update_product()
        elif choice == 4:
            delete_product()
        elif choice == 5:
            return

def add_product():
    clear_screen()
    print("╔════════════════════════════════════════╗")
    print("║            ADD PRODUCT               ║")
    print("╚════════════════════════════════════════╝")
    
    try:
        barcode = input("Barcode (leave empty if none): ").strip()
        name = input("Product Name: ").strip()
        if not name:
            print("Product name cannot be empty!")
            input("\nPress Enter to continue...")
            return
            
        price = float(input("Price: "))
        if price <= 0:
            print("Price must be positive!")
            input("\nPress Enter to continue...")
            return
            
        stock = int(input("Stock: "))
        if stock < 0:
            print("Stock cannot be negative!")
            input("\nPress Enter to continue...")
            return
            
        conn = get_db_connection()
        conn.execute('INSERT INTO products (barcode, name, price, stock) VALUES (?, ?, ?, ?)',
                    (barcode if barcode else None, name, price, stock))
        conn.commit()
        conn.close()
        
        print(f"\nProduct '{name}' added successfully!")
    except sqlite3.IntegrityError:
        print("Error: Barcode already exists.")
    except ValueError:
        print("Error: Invalid input for price or stock.")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    input("\nPress Enter to continue...")

def view_products():
    clear_screen()
    print("╔════════════════════════════════════════╗")
    print("║             PRODUCT LIST             ║")
    print("╚════════════════════════════════════════╝")
    
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products ORDER BY name').fetchall()
    conn.close()
    
    if not products:
        print("\nNo products found.")
    else:
        print("\nID  Barcode       Name                 Price     Stock")
        print("======================================================")
        for product in products:
            print(f"{product['id']:<3} {product['barcode'] or 'N/A':<12} {product['name']:<20} {product['price']:>8.2f} {product['stock']:>8}")
    
    input("\nPress Enter to continue...")

def update_product():
    clear_screen()
    print("╔════════════════════════════════════════╗")
    print("║           UPDATE PRODUCT             ║")
    print("╚════════════════════════════════════════╝")
    
    view_products()
    
    try:
        product_id = int(input("\nEnter product ID to update (0 to cancel): "))
        if product_id == 0:
            return
            
        conn = get_db_connection()
        product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
        
        if not product:
            print("Product not found.")
            conn.close()
            input("\nPress Enter to continue...")
            return
        
        print(f"\nCurrent details for {product['name']}:")
        print(f"Barcode: {product['barcode'] or 'N/A'}")
        print(f"Price: {product['price']}")
        print(f"Stock: {product['stock']}")
        
        barcode = input(f"\nNew barcode (current: {product['barcode'] or 'N/A'}, leave empty to keep): ")
        name = input(f"New name (current: {product['name']}, leave empty to keep): ")
        price = input(f"New price (current: {product['price']}, leave empty to keep): ")
        stock = input(f"New stock (current: {product['stock']}, leave empty to keep): ")
        
        update_fields = []
        update_values = []
        
        if barcode:
            update_fields.append("barcode = ?")
            update_values.append(barcode if barcode != 'N/A' else None)
        if name:
            update_fields.append("name = ?")
            update_values.append(name)
        if price:
            update_fields.append("price = ?")
            update_values.append(float(price))
        if stock:
            update_fields.append("stock = ?")
            update_values.append(int(stock))
        
        if update_fields:
            update_values.append(product_id)
            query = f"UPDATE products SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            conn.execute(query, update_values)
            conn.commit()
            print("\nProduct updated successfully!")
        else:
            print("\nNo changes made.")
        
        conn.close()
    except ValueError:
        print("Error: Invalid input for price or stock.")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    input("\nPress Enter to continue...")

def delete_product():
    clear_screen()
    print("╔════════════════════════════════════════╗")
    print("║           DELETE PRODUCT             ║")
    print("╚════════════════════════════════════════╝")
    
    view_products()
    
    try:
        product_id = int(input("\nEnter product ID to delete (0 to cancel): "))
        if product_id == 0:
            return
            
        conn = get_db_connection()
        product = conn.execute('SELECT name FROM products WHERE id = ?', (product_id,)).fetchone()
        
        if not product:
            print("Product not found.")
        else:
            confirm = input(f"Are you sure you want to delete '{product['name']}'? (y/n): ").lower()
            if confirm == 'y':
                conn.execute('DELETE FROM products WHERE id = ?', (product_id,))
                conn.commit()
                print("Product deleted successfully!")
            else:
                print("Deletion canceled.")
        
        conn.close()
    except ValueError:
        print("Error: Invalid product ID.")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    input("\nPress Enter to continue...")

# Process Sale
def process_sale(user):
    current_sale = {'items': [], 'customer_id': None}
    
    while True:
        clear_screen()
        print("╔════════════════════════════════════════╗")
        print("║             PROCESS SALE              ║")
        print("╚════════════════════════════════════════╝")
        
        # Display current sale items
        if current_sale['items']:
            print("\nID  Product Name          Price     Qty     Subtotal")
            print("====================================================")
            total = 0
            for item in current_sale['items']:
                subtotal = item['price'] * item['quantity']
                total += subtotal
                print(f"{item['id']:<3} {item['name']:<20} {item['price']:>8.2f} {item['quantity']:>8} {subtotal:>10.2f}")
            print("====================================================")
            print(f"Total: {total:>42.2f}\n")
        else:
            print("\nNo items in current sale.\n")
        
        if current_sale['items']:
            print("1. Remove product from sale")
            print("2. Finalize sale")
            print("3. Cancel sale")
            choices = [1, 2, 3]
        else:
            print("2. Finalize sale (no items)")
            print("3. Cancel sale")
            choices = [2, 3]
        
        print("\nScan barcode to add product...")
        
        try:
            user_input = input("\nEnter barcode or option number: ").strip()
            
            if user_input == '1' and 1 in choices:
                remove_product(current_sale)
            elif user_input == '2':
                finalize_sale(current_sale, user)
                return
            elif user_input == '3':
                confirm = input("Are you sure you want to cancel this sale? (y/n): ").lower()
                if confirm == 'y':
                    print("Sale canceled.")
                    time.sleep(1)
                    return
            elif user_input:  # Barcode scan
                conn = get_db_connection()
                product = conn.execute('SELECT * FROM products WHERE barcode = ?', (user_input,)).fetchone()
                conn.close()
                
                if product:
                    # Check if product already in sale
                    item_found = False
                    for item in current_sale['items']:
                        if item['id'] == product['id']:
                            item['quantity'] += 1
                            item_found = True
                            break
                    
                    if not item_found:
                        current_sale['items'].append({
                            'id': product['id'],
                            'name': product['name'],
                            'price': product['price'],
                            'quantity': 1
                        })
                    # No confirmation needed, just continue to next scan
                else:
                    print("\nProduct not found. Please try again.")
                    time.sleep(1)  # Brief pause to see the message
        except Exception as e:
            print(f"\nError: {str(e)}")
            time.sleep(1)  # Brief pause to see the error message


def scan_product(current_sale):
    barcode = input("\nEnter barcode (or 0 to cancel): ")
    if barcode == '0':
        return
    
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE barcode = ?', (barcode,)).fetchone()
    conn.close()
    
    if not product:
        print("Product not found.")
        input("\nPress Enter to continue...")
        return
    
    try:
        quantity = int(input(f"Enter quantity for {product['name']} (available: {product['stock']}): "))
        if quantity <= 0:
            print("Quantity must be positive.")
        elif quantity > product['stock']:
            print("Not enough stock available.")
        else:
            # Check if product already in sale
            for item in current_sale['items']:
                if item['id'] == product['id']:
                    item['quantity'] += quantity
                    break
            else:
                current_sale['items'].append({
                    'id': product['id'],
                    'name': product['name'],
                    'price': product['price'],
                    'quantity': quantity
                })
            print(f"Added {quantity} x {product['name']} to sale.")
    except ValueError:
        print("Invalid quantity.")
    
    input("\nPress Enter to continue...")

def add_product_by_id(current_sale):
    view_products()
    
    try:
        product_id = int(input("\nEnter product ID to add (0 to cancel): "))
        if product_id == 0:
            return
            
        conn = get_db_connection()
        product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
        conn.close()
        
        if not product:
            print("Product not found.")
            input("\nPress Enter to continue...")
            return
        
        try:
            quantity = int(input(f"Enter quantity for {product['name']} (available: {product['stock']}): "))
            if quantity <= 0:
                print("Quantity must be positive.")
            elif quantity > product['stock']:
                print("Not enough stock available.")
            else:
                # Check if product already in sale
                for item in current_sale['items']:
                    if item['id'] == product['id']:
                        item['quantity'] += quantity
                        break
                else:
                    current_sale['items'].append({
                        'id': product['id'],
                        'name': product['name'],
                        'price': product['price'],
                        'quantity': quantity
                    })
                print(f"Added {quantity} x {product['name']} to sale.")
        except ValueError:
            print("Invalid quantity.")
    except ValueError:
        print("Invalid product ID.")
    
    input("\nPress Enter to continue...")

def remove_product(current_sale):
    print("\nCurrent Sale Items:")
    for i, item in enumerate(current_sale['items'], 1):
        print(f"{i}. {item['name']} - {item['quantity']} x {item['price']}")
    
    try:
        choice = int(input("\nEnter item number to remove (0 to cancel): "))
        if choice == 0:
            return
        elif 1 <= choice <= len(current_sale['items']):
            item = current_sale['items'][choice-1]
            quantity = int(input(f"Enter quantity to remove (current: {item['quantity']}): "))
            
            if quantity <= 0:
                print("Quantity must be positive.")
            elif quantity > item['quantity']:
                print("Cannot remove more than current quantity.")
            else:
                item['quantity'] -= quantity
                if item['quantity'] <= 0:
                    current_sale['items'].pop(choice-1)
                print("Item quantity updated.")
        else:
            print("Invalid item number.")
    except ValueError:
        print("Invalid input.")
    
    input("\nPress Enter to continue...")

def finalize_sale(current_sale, user):
    if not current_sale['items']:
        print("No items in current sale to finalize.")
        input("\nPress Enter to continue...")
        return
    
    # Calculate total
    total = sum(item['price'] * item['quantity'] for item in current_sale['items'])
    
    # Ask for customer
    print("\nCustomer Options:")
    print("1. New customer")
    print("2. Existing customer")
    print("3. No customer")
    
    try:
        customer_choice = int(input("Enter choice (1-3): "))
        if customer_choice == 1:
            current_sale['customer_id'] = add_customer_during_sale()
        elif customer_choice == 2:
            current_sale['customer_id'] = select_customer()
        elif customer_choice == 3:
            current_sale['customer_id'] = None
        else:
            print("Invalid choice. Defaulting to no customer.")
            current_sale['customer_id'] = None
    except ValueError:
        print("Invalid input. Defaulting to no customer.")
        current_sale['customer_id'] = None
    
    # Payment
    print(f"\nTotal Amount: {total:.2f}")
    while True:
        try:
            amount_paid = float(input("Enter amount paid: "))
            if amount_paid < total:
                print("Amount paid cannot be less than total.")
                continue
            
            change = amount_paid - total
            print(f"Change: {change:.2f}")
            
            payment_method = input("Payment method (cash/card): ").lower()
            if payment_method not in ['cash', 'card']:
                payment_method = 'cash'
            
            confirm = input("Confirm sale? (y/n): ").lower()
            if confirm != 'y':
                print("Sale canceled.")
                return
            
            # Process sale in database
            conn = get_db_connection()
            
            # Create sale record
            conn.execute('''
                INSERT INTO sales (customer_id, user_id, total_amount, amount_paid, change_given, payment_method)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (current_sale['customer_id'], user['id'], total, amount_paid, change, payment_method))
            
            # Get the sale ID
            sale_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
            
            # Add sale items and update stock
            for item in current_sale['items']:
                conn.execute('''
                    INSERT INTO sale_items (sale_id, product_id, quantity, price)
                    VALUES (?, ?, ?, ?)
                ''', (sale_id, item['id'], item['quantity'], item['price']))
                
                conn.execute('''
                    UPDATE products SET stock = stock - ? WHERE id = ?
                ''', (item['quantity'], item['id']))
            
            conn.commit()
            conn.close()
            
            print("\nSale completed successfully!")
            print(f"Sale ID: {sale_id}")
            print(f"Total: {total:.2f}")
            print(f"Paid: {amount_paid:.2f}")
            print(f"Change: {change:.2f}")
            
            # Reset current sale
            current_sale['items'] = []
            current_sale['customer_id'] = None
            
            break
        except ValueError:
            print("Invalid amount. Please enter a valid number.")
    
    input("\nPress Enter to continue...")

def add_customer_during_sale():
    clear_screen()
    print("╔════════════════════════════════════════╗")
    print("║          ADD NEW CUSTOMER            ║")
    print("╚════════════════════════════════════════╝")
    
    name = input("Customer Name: ")
    phone = input("Phone (optional): ")
    email = input("Email (optional): ")
    address = input("Address (optional): ")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO customers (name, phone, email, address)
        VALUES (?, ?, ?, ?)
    ''', (name, phone or None, email or None, address or None))
    
    customer_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f"\nCustomer '{name}' added successfully with ID: {customer_id}")
    input("\nPress Enter to continue...")
    return customer_id

def select_customer():
    clear_screen()
    print("╔════════════════════════════════════════╗")
    print("║         SELECT CUSTOMER              ║")
    print("╚════════════════════════════════════════╝")
    
    conn = get_db_connection()
    customers = conn.execute('SELECT id, name, phone FROM customers ORDER BY name').fetchall()
    conn.close()
    
    if not customers:
        print("\nNo customers found.")
        input("\nPress Enter to continue...")
        return None
    
    print("\nID  Name                 Phone")
    print("======================================")
    for customer in customers:
        print(f"{customer['id']:<3} {customer['name']:<20} {customer['phone'] or 'N/A'}")
    
    try:
        customer_id = int(input("\nEnter customer ID (0 to cancel): "))
        if customer_id == 0:
            return None
        
        conn = get_db_connection()
        customer = conn.execute('SELECT id FROM customers WHERE id = ?', (customer_id,)).fetchone()
        conn.close()
        
        if not customer:
            print("Customer not found.")
            input("\nPress Enter to continue...")
            return None
        
        return customer_id
    except ValueError:
        print("Invalid customer ID.")
        input("\nPress Enter to continue...")
        return None

# Customer Management
def customer_management():
    while True:
        clear_screen()
        print("╔════════════════════════════════════════╗")
        print("║         CUSTOMER MANAGEMENT          ║")
        print("╚════════════════════════════════════════╝")
        print("\n1. Add Customer")
        print("2. View Customers")
        print("3. Update Customer")
        print("4. Delete Customer")
        print("5. Back to Main Menu")
        
        try:
            choice = int(input("\nEnter your choice (1-5): "))
            if choice not in range(1, 6):
                raise ValueError
        except ValueError:
            input("Invalid choice. Press Enter to try again...")
            continue
        
        if choice == 1:
            add_customer()
        elif choice == 2:
            view_customers()
        elif choice == 3:
            update_customer()
        elif choice == 4:
            delete_customer()
        elif choice == 5:
            return

def add_customer():
    clear_screen()
    print("╔════════════════════════════════════════╗")
    print("║           ADD CUSTOMER               ║")
    print("╚════════════════════════════════════════╝")
    
    name = input("Name: ")
    phone = input("Phone: ")
    email = input("Email: ")
    address = input("Address: ")
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO customers (name, phone, email, address)
        VALUES (?, ?, ?, ?)
    ''', (name, phone or None, email or None, address or None))
    conn.commit()
    conn.close()
    
    print(f"\nCustomer '{name}' added successfully!")
    input("\nPress Enter to continue...")

def view_customers():
    clear_screen()
    print("╔════════════════════════════════════════╗")
    print("║           CUSTOMER LIST              ║")
    print("╚════════════════════════════════════════╝")
    
    conn = get_db_connection()
    customers = conn.execute('SELECT * FROM customers ORDER BY name').fetchall()
    conn.close()
    
    if not customers:
        print("\nNo customers found.")
    else:
        print("\nID  Name                 Phone          Email")
        print("====================================================")
        for customer in customers:
            print(f"{customer['id']:<3} {customer['name']:<20} {customer['phone'] or 'N/A':<14} {customer['email'] or 'N/A'}")
    
    input("\nPress Enter to continue...")

def update_customer():
    clear_screen()
    print("╔════════════════════════════════════════╗")
    print("║          UPDATE CUSTOMER            ║")
    print("╚════════════════════════════════════════╝")
    
    view_customers()
    
    try:
        customer_id = int(input("\nEnter customer ID to update (0 to cancel): "))
        if customer_id == 0:
            return
            
        conn = get_db_connection()
        customer = conn.execute('SELECT * FROM customers WHERE id = ?', (customer_id,)).fetchone()
        
        if not customer:
            print("Customer not found.")
            conn.close()
            input("\nPress Enter to continue...")
            return
        
        print(f"\nCurrent details for {customer['name']}:")
        print(f"Phone: {customer['phone'] or 'N/A'}")
        print(f"Email: {customer['email'] or 'N/A'}")
        print(f"Address: {customer['address'] or 'N/A'}")
        
        name = input(f"\nNew name (current: {customer['name']}, leave empty to keep): ")
        phone = input(f"New phone (current: {customer['phone'] or 'N/A'}, leave empty to keep): ")
        email = input(f"New email (current: {customer['email'] or 'N/A'}, leave empty to keep): ")
        address = input(f"New address (current: {customer['address'] or 'N/A'}, leave empty to keep): ")
        
        update_fields = []
        update_values = []
        
        if name:
            update_fields.append("name = ?")
            update_values.append(name)
        if phone:
            update_fields.append("phone = ?")
            update_values.append(phone if phone != 'N/A' else None)
        if email:
            update_fields.append("email = ?")
            update_values.append(email if email != 'N/A' else None)
        if address:
            update_fields.append("address = ?")
            update_values.append(address if address != 'N/A' else None)
        
        if update_fields:
            update_values.append(customer_id)
            query = f"UPDATE customers SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            conn.execute(query, update_values)
            conn.commit()
            print("\nCustomer updated successfully!")
        else:
            print("\nNo changes made.")
        
        conn.close()
    except ValueError:
        print("Error: Invalid customer ID.")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    input("\nPress Enter to continue...")

def delete_customer():
    clear_screen()
    print("╔════════════════════════════════════════╗")
    print("║          DELETE CUSTOMER            ║")
    print("╚════════════════════════════════════════╝")
    
    view_customers()
    
    try:
        customer_id = int(input("\nEnter customer ID to delete (0 to cancel): "))
        if customer_id == 0:
            return
            
        conn = get_db_connection()
        customer = conn.execute('SELECT name FROM customers WHERE id = ?', (customer_id,)).fetchone()
        
        if not customer:
            print("Customer not found.")
        else:
            # Check if customer has sales
            sales = conn.execute('SELECT COUNT(*) FROM sales WHERE customer_id = ?', (customer_id,)).fetchone()[0]
            if sales > 0:
                print(f"Cannot delete customer '{customer['name']}' because they have {sales} associated sales.")
            else:
                confirm = input(f"Are you sure you want to delete '{customer['name']}'? (y/n): ").lower()
                if confirm == 'y':
                    conn.execute('DELETE FROM customers WHERE id = ?', (customer_id,))
                    conn.commit()
                    print("Customer deleted successfully!")
                else:
                    print("Deletion canceled.")
        
        conn.close()
    except ValueError:
        print("Error: Invalid customer ID.")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    input("\nPress Enter to continue...")

# Sale History
def sale_history():
    while True:
        clear_screen()
        print("╔════════════════════════════════════════╗")
        print("║             SALE HISTORY             ║")
        print("╚════════════════════════════════════════╝")
        print("\n1. View All Sales")
        print("2. View Sales by Date Range")
        print("3. View Sale Details")
        print("4. Delete Sale")
        print("5. Delete All Sales")
        print("6. Back to Main Menu")
        
        try:
            choice = int(input("\nEnter your choice (1-6): "))
            if choice not in range(1, 7):
                raise ValueError
        except ValueError:
            input("Invalid choice. Press Enter to try again...")
            continue
        
        if choice == 1:
            view_all_sales()
        elif choice == 2:
            view_sales_by_date()
        elif choice == 3:
            view_sale_details()
        elif choice == 4:
            delete_sale()
        elif choice == 5:
            delete_all_sales()
        elif choice == 6:
            return

def view_all_sales():
    clear_screen()
    print("╔════════════════════════════════════════╗")
    print("║            ALL SALES                ║")
    print("╚════════════════════════════════════════╝")
    
    conn = get_db_connection()
    sales = conn.execute('''
        SELECT s.id, s.sale_date, s.total_amount, 
               u.full_name as cashier, 
               c.name as customer
        FROM sales s
        LEFT JOIN users u ON s.user_id = u.id
        LEFT JOIN customers c ON s.customer_id = c.id
        ORDER BY s.sale_date DESC
    ''').fetchall()
    conn.close()
    
    if not sales:
        print("\nNo sales found.")
    else:
        print("\nID  Date                Customer            Cashier          Total")
        print("===================================================================")
        for sale in sales:
            date_str = datetime.strptime(sale['sale_date'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M')
            print(f"{sale['id']:<3} {date_str:<19} {sale['customer'] or 'N/A':<18} {sale['cashier']:<16} {sale['total_amount']:>8.2f}")
    
    input("\nPress Enter to continue...")

def view_sales_by_date():
    clear_screen()
    print("╔════════════════════════════════════════╗")
    print("║        SALES BY DATE RANGE          ║")
    print("╚════════════════════════════════════════╝")
    
    try:
        start_date = input("Enter start date (YYYY-MM-DD, leave empty for all): ")
        end_date = input("Enter end date (YYYY-MM-DD, leave empty for today): ")
        
        query = '''
            SELECT s.id, s.sale_date, s.total_amount, 
                   u.full_name as cashier, 
                   c.name as customer
            FROM sales s
            LEFT JOIN users u ON s.user_id = u.id
            LEFT JOIN customers c ON s.customer_id = c.id
        '''
        params = []
        
        if start_date or end_date:
            query += " WHERE "
            conditions = []
            if start_date:
                conditions.append("s.sale_date >= ?")
                params.append(f"{start_date} 00:00:00")
            if end_date:
                conditions.append("s.sale_date <= ?")
                params.append(f"{end_date} 23:59:59")
            query += " AND ".join(conditions)
        
        query += " ORDER BY s.sale_date DESC"
        
        conn = get_db_connection()
        sales = conn.execute(query, params).fetchall()
        conn.close()
        
        clear_screen()
        print("╔════════════════════════════════════════╗")
        if start_date or end_date:
            date_range = f"From {start_date or 'beginning'} to {end_date or 'today'}"
            print(f"║        SALES {date_range:<26}║")
        else:
            print("║            ALL SALES                ║")
        print("╚════════════════════════════════════════╝")
        
        if not sales:
            print("\nNo sales found for the selected date range.")
        else:
            print("\nID  Date                Customer            Cashier          Total")
            print("===================================================================")
            for sale in sales:
                date_str = datetime.strptime(sale['sale_date'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M')
                print(f"{sale['id']:<3} {date_str:<19} {sale['customer'] or 'N/A':<18} {sale['cashier']:<16} {sale['total_amount']:>8.2f}")
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
    
    input("\nPress Enter to continue...")

def view_sale_details():
    view_all_sales()
    
    try:
        sale_id = int(input("\nEnter sale ID to view details (0 to cancel): "))
        if sale_id == 0:
            return
            
        conn = get_db_connection()
        
        # Get sale header
        sale = conn.execute('''
            SELECT s.*, u.full_name as cashier, c.name as customer
            FROM sales s
            LEFT JOIN users u ON s.user_id = u.id
            LEFT JOIN customers c ON s.customer_id = c.id
            WHERE s.id = ?
        ''', (sale_id,)).fetchone()
        
        if not sale:
            print("Sale not found.")
            conn.close()
            input("\nPress Enter to continue...")
            return
        
        # Get sale items
        items = conn.execute('''
            SELECT si.*, p.name as product_name
            FROM sale_items si
            JOIN products p ON si.product_id = p.id
            WHERE si.sale_id = ?
        ''', (sale_id,)).fetchall()
        
        conn.close()
        
        clear_screen()
        print("╔════════════════════════════════════════╗")
        print(f"║          SALE DETAILS - ID {sale_id:<12}      ║")
        print("╚════════════════════════════════════════╝")
        
        print(f"\nDate: {sale['sale_date']}")
        print(f"Cashier: {sale['cashier']}")
        print(f"Customer: {sale['customer'] or 'N/A'}")
        print(f"Payment Method: {sale['payment_method'].capitalize()}")
        print("\nItems:")
        print("Product Name          Price     Qty     Subtotal")
        print("================================================")
        total = 0
        for item in items:
            subtotal = item['price'] * item['quantity']
            total += subtotal
            print(f"{item['product_name']:<20} {item['price']:>8.2f} {item['quantity']:>8} {subtotal:>10.2f}")
        print("================================================")
        print(f"Total: {total:>42.2f}")
        print(f"Amount Paid: {sale['amount_paid']:>36.2f}")
        print(f"Change Given: {sale['change_given']:>35.2f}")
    except ValueError:
        print("Invalid sale ID.")
    
    input("\nPress Enter to continue...")

def delete_sale():
    view_all_sales()
    
    try:
        sale_id = int(input("\nEnter sale ID to delete (0 to cancel): "))
        if sale_id == 0:
            return
            
        conn = get_db_connection()
        sale = conn.execute('SELECT id FROM sales WHERE id = ?', (sale_id,)).fetchone()
        
        if not sale:
            print("Sale not found.")
        else:
            confirm = input("Are you sure you want to delete this sale? This cannot be undone. (y/n): ").lower()
            if confirm == 'y':
                # First, restore product stock
                items = conn.execute('SELECT product_id, quantity FROM sale_items WHERE sale_id = ?', (sale_id,)).fetchall()
                for item in items:
                    conn.execute('UPDATE products SET stock = stock + ? WHERE id = ?', (item['quantity'], item['product_id']))
                
                # Then delete sale items
                conn.execute('DELETE FROM sale_items WHERE sale_id = ?', (sale_id,))
                
                # Finally delete the sale
                conn.execute('DELETE FROM sales WHERE id = ?', (sale_id,))
                
                conn.commit()
                print("Sale deleted successfully!")
            else:
                print("Deletion canceled.")
        
        conn.close()
    except ValueError:
        print("Invalid sale ID.")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    input("\nPress Enter to continue...")

def delete_all_sales():
    clear_screen()
    print("╔════════════════════════════════════════╗")
    print("║         DELETE ALL SALES            ║")
    print("╚════════════════════════════════════════╝")
    
    confirm = input("\nWARNING: This will delete ALL sales records and cannot be undone!\nAre you absolutely sure? (y/n): ").lower()
    if confirm != 'y':
        print("Operation canceled.")
        input("\nPress Enter to continue...")
        return
    
    try:
        conn = get_db_connection()
        
        # First, restore all product stock
        items = conn.execute('''
            SELECT product_id, SUM(quantity) as total_quantity
            FROM sale_items
            GROUP BY product_id
        ''').fetchall()
        
        for item in items:
            conn.execute('UPDATE products SET stock = stock + ? WHERE id = ?', (item['total_quantity'], item['product_id']))
        
        # Then delete all sale items
        conn.execute('DELETE FROM sale_items')
        
        # Finally delete all sales
        conn.execute('DELETE FROM sales')
        
        conn.commit()
        conn.close()
        
        print("All sales records have been deleted.")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    input("\nPress Enter to continue...")

# Reports
def reports():
    while True:
        clear_screen()
        print("╔════════════════════════════════════════╗")
        print("║               REPORTS                ║")
        print("╚════════════════════════════════════════╝")
        print("\n1. Sales Summary")
        print("2. Product Sales")
        print("3. Daily Sales")
        print("4. Monthly Sales")
        print("5. Back to Main Menu")
        
        try:
            choice = int(input("\nEnter your choice (1-5): "))
            if choice not in range(1, 6):
                raise ValueError
        except ValueError:
            input("Invalid choice. Press Enter to try again...")
            continue
        
        if choice == 1:
            sales_summary()
        elif choice == 2:
            product_sales()
        elif choice == 3:
            daily_sales()
        elif choice == 4:
            monthly_sales()
        elif choice == 5:
            return

def sales_summary():
    clear_screen()
    print("╔════════════════════════════════════════╗")
    print("║            SALES SUMMARY             ║")
    print("╚════════════════════════════════════════╝")
    
    try:
        start_date = input("\nEnter start date (YYYY-MM-DD, leave empty for all): ")
        end_date = input("Enter end date (YYYY-MM-DD, leave empty for today): ")
        
        query = '''
            SELECT 
                COUNT(*) as total_sales,
                SUM(total_amount) as total_revenue,
                AVG(total_amount) as avg_sale,
                MIN(total_amount) as min_sale,
                MAX(total_amount) as max_sale
            FROM sales
        '''
        params = []
        
        if start_date or end_date:
            query += " WHERE "
            conditions = []
            if start_date:
                conditions.append("sale_date >= ?")
                params.append(f"{start_date} 00:00:00")
            if end_date:
                conditions.append("sale_date <= ?")
                params.append(f"{end_date} 23:59:59")
            query += " AND ".join(conditions)
        
        conn = get_db_connection()
        summary = conn.execute(query, params).fetchone()
        conn.close()
        
        print("\nSummary:")
        print("=================================")
        print(f"Total Sales:      {summary['total_sales']:>10}")
        print(f"Total Revenue:    {summary['total_revenue'] or 0:>10.2f}")
        print(f"Average Sale:     {summary['avg_sale'] or 0:>10.2f}")
        print(f"Smallest Sale:    {summary['min_sale'] or 0:>10.2f}")
        print(f"Largest Sale:     {summary['max_sale'] or 0:>10.2f}")
    except Exception as e:
        print(f"Error generating report: {str(e)}")
    
    input("\nPress Enter to continue...")

def product_sales():
    clear_screen()
    print("╔════════════════════════════════════════╗")
    print("║           PRODUCT SALES             ║")
    print("╚════════════════════════════════════════╝")
    
    try:
        start_date = input("\nEnter start date (YYYY-MM-DD, leave empty for all): ")
        end_date = input("Enter end date (YYYY-MM-DD, leave empty for today): ")
        
        query = '''
            SELECT 
                p.id,
                p.name,
                SUM(si.quantity) as total_quantity,
                SUM(si.quantity * si.price) as total_revenue
            FROM sale_items si
            JOIN products p ON si.product_id = p.id
            JOIN sales s ON si.sale_id = s.id
        '''
        params = []
        
        if start_date or end_date:
            query += " WHERE "
            conditions = []
            if start_date:
                conditions.append("s.sale_date >= ?")
                params.append(f"{start_date} 00:00:00")
            if end_date:
                conditions.append("s.sale_date <= ?")
                params.append(f"{end_date} 23:59:59")
            query += " AND ".join(conditions)
        
        query += '''
            GROUP BY p.id, p.name
            ORDER BY total_revenue DESC
        '''
        
        conn = get_db_connection()
        products = conn.execute(query, params).fetchall()
        conn.close()
        
        print("\nProduct Sales:")
        print("ID  Product Name          Qty Sold    Revenue")
        print("==============================================")
        for product in products:
            print(f"{product['id']:<3} {product['name']:<20} {product['total_quantity']:>8} {product['total_revenue']:>12.2f}")
    except Exception as e:
        print(f"Error generating report: {str(e)}")
    
    input("\nPress Enter to continue...")

def daily_sales():
    clear_screen()
    print("╔════════════════════════════════════════╗")
    print("║            DAILY SALES              ║")
    print("╚════════════════════════════════════════╝")
    
    try:
        start_date = input("\nEnter start date (YYYY-MM-DD, leave empty for all): ")
        end_date = input("Enter end date (YYYY-MM-DD, leave empty for today): ")
        
        query = '''
            SELECT 
                DATE(sale_date) as sale_day,
                COUNT(*) as total_sales,
                SUM(total_amount) as total_revenue
            FROM sales
        '''
        params = []
        
        if start_date or end_date:
            query += " WHERE "
            conditions = []
            if start_date:
                conditions.append("sale_date >= ?")
                params.append(f"{start_date} 00:00:00")
            if end_date:
                conditions.append("sale_date <= ?")
                params.append(f"{end_date} 23:59:59")
            query += " AND ".join(conditions)
        
        query += '''
            GROUP BY DATE(sale_date)
            ORDER BY sale_day DESC
        '''
        
        conn = get_db_connection()
        daily = conn.execute(query, params).fetchall()
        conn.close()
        
        print("\nDaily Sales:")
        print("Date         Sales    Revenue")
        print("===============================")
        for day in daily:
            print(f"{day['sale_day']} {day['total_sales']:>6} {day['total_revenue']:>12.2f}")
    except Exception as e:
        print(f"Error generating report: {str(e)}")
    
    input("\nPress Enter to continue...")

def monthly_sales():
    clear_screen()
    print("╔════════════════════════════════════════╗")
    print("║           MONTHLY SALES             ║")
    print("╚════════════════════════════════════════╝")
    
    try:
        start_date = input("\nEnter start date (YYYY-MM, leave empty for all): ")
        end_date = input("Enter end date (YYYY-MM, leave empty for current month): ")
        
        query = '''
            SELECT 
                strftime('%Y-%m', sale_date) as sale_month,
                COUNT(*) as total_sales,
                SUM(total_amount) as total_revenue
            FROM sales
        '''
        params = []
        
        if start_date or end_date:
            query += " WHERE "
            conditions = []
            if start_date:
                conditions.append("sale_date >= ?")
                params.append(f"{start_date}-01 00:00:00")
            if end_date:
                conditions.append("sale_date <= ?")
                params.append(f"{end_date}-31 23:59:59")
            query += " AND ".join(conditions)
        
        query += '''
            GROUP BY strftime('%Y-%m', sale_date)
            ORDER BY sale_month DESC
        '''
        
        conn = get_db_connection()
        monthly = conn.execute(query, params).fetchall()
        conn.close()
        
        print("\nMonthly Sales:")
        print("Month     Sales    Revenue")
        print("===============================")
        for month in monthly:
            print(f"{month['sale_month']} {month['total_sales']:>6} {month['total_revenue']:>12.2f}")
    except Exception as e:
        print(f"Error generating report: {str(e)}")
    
    input("\nPress Enter to continue...")

# System Settings (Admin only)
def system_settings():
    while True:
        clear_screen()
        print("╔════════════════════════════════════════╗")
        print("║           SYSTEM SETTINGS            ║")
        print("╚════════════════════════════════════════╝")
        print("\n1. Change Password")
        print("2. Manage Users")
        print("3. Backup Database")
        print("4. Restore Database")
        print("5. Back to Main Menu")
        
        try:
            choice = int(input("\nEnter your choice (1-5): "))
            if choice not in range(1, 6):
                raise ValueError
        except ValueError:
            input("Invalid choice. Press Enter to try again...")
            continue
        
        if choice == 1:
            change_password()
        elif choice == 2:
            manage_users()
        elif choice == 3:
            backup_database()
        elif choice == 4:
            restore_database()
        elif choice == 5:
            return

def change_password():
    clear_screen()
    print("╔════════════════════════════════════════╗")
    print("║          CHANGE PASSWORD             ║")
    print("╚════════════════════════════════════════╝")
    
    current_user = login()  # Re-login to verify
    
    new_password = getpass.getpass("New Password: ")
    confirm_password = getpass.getpass("Confirm New Password: ")
    
    if new_password != confirm_password:
        print("Passwords do not match.")
        input("\nPress Enter to continue...")
        return
    
    try:
        conn = get_db_connection()
        conn.execute('UPDATE users SET password = ? WHERE id = ?', (new_password, current_user['id']))
        conn.commit()
        conn.close()
        
        print("\nPassword changed successfully!")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    input("\nPress Enter to continue...")

def manage_users():
    while True:
        clear_screen()
        print("╔════════════════════════════════════════╗")
        print("║            MANAGE USERS              ║")
        print("╚════════════════════════════════════════╝")
        print("\n1. Add User")
        print("2. View Users")
        print("3. Update User")
        print("4. Delete User")
        print("5. Back to System Settings")
        
        try:
            choice = int(input("\nEnter your choice (1-5): "))
            if choice not in range(1, 6):
                raise ValueError
        except ValueError:
            input("Invalid choice. Press Enter to try again...")
            continue
        
        if choice == 1:
            add_user()
        elif choice == 2:
            view_users()
        elif choice == 3:
            update_user()
        elif choice == 4:
            delete_user()
        elif choice == 5:
            return

def add_user():
    clear_screen()
    print("╔════════════════════════════════════════╗")
    print("║              ADD USER                ║")
    print("╚════════════════════════════════════════╝")
    
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    full_name = input("Full Name: ")
    role = input("Role (admin/cashier): ").lower()
    
    if role not in ['admin', 'cashier']:
        role = 'cashier'
    
    try:
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO users (username, password, full_name, role)
            VALUES (?, ?, ?, ?)
        ''', (username, password, full_name, role))
        conn.commit()
        conn.close()
        
        print(f"\nUser '{username}' added successfully!")
    except sqlite3.IntegrityError:
        print("Error: Username already exists.")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    input("\nPress Enter to continue...")

def view_users():
    clear_screen()
    print("╔════════════════════════════════════════╗")
    print("║             USER LIST               ║")
    print("╚════════════════════════════════════════╝")
    
    conn = get_db_connection()
    users = conn.execute('SELECT id, username, full_name, role FROM users ORDER BY username').fetchall()
    conn.close()
    
    if not users:
        print("\nNo users found.")
    else:
        print("\nID  Username       Full Name          Role")
        print("============================================")
        for user in users:
            print(f"{user['id']:<3} {user['username']:<14} {user['full_name']:<18} {user['role']}")
    
    input("\nPress Enter to continue...")

def update_user():
    clear_screen()
    print("╔════════════════════════════════════════╗")
    print("║            UPDATE USER              ║")
    print("╚════════════════════════════════════════╝")
    
    view_users()
    
    try:
        user_id = int(input("\nEnter user ID to update (0 to cancel): "))
        if user_id == 0:
            return
            
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        
        if not user:
            print("User not found.")
            conn.close()
            input("\nPress Enter to continue...")
            return
        
        print(f"\nCurrent details for {user['username']}:")
        print(f"Full Name: {user['full_name']}")
        print(f"Role: {user['role']}")
        
        username = input(f"\nNew username (current: {user['username']}, leave empty to keep): ")
        full_name = input(f"New full name (current: {user['full_name']}, leave empty to keep): ")
        role = input(f"New role (current: {user['role']}, leave empty to keep): ").lower()
        
        update_fields = []
        update_values = []
        
        if username:
            update_fields.append("username = ?")
            update_values.append(username)
        if full_name:
            update_fields.append("full_name = ?")
            update_values.append(full_name)
        if role and role in ['admin', 'cashier']:
            update_fields.append("role = ?")
            update_values.append(role)
        
        if update_fields:
            update_values.append(user_id)
            query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
            conn.execute(query, update_values)
            conn.commit()
            print("\nUser updated successfully!")
        else:
            print("\nNo changes made.")
        
        conn.close()
    except sqlite3.IntegrityError:
        print("Error: Username already exists.")
    except ValueError:
        print("Error: Invalid user ID.")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    input("\nPress Enter to continue...")

def delete_user():
    clear_screen()
    print("╔════════════════════════════════════════╗")
    print("║            DELETE USER              ║")
    print("╚════════════════════════════════════════╝")
    
    view_users()
    
    try:
        user_id = int(input("\nEnter user ID to delete (0 to cancel): "))
        if user_id == 0:
            return
            
        conn = get_db_connection()
        user = conn.execute('SELECT username FROM users WHERE id = ?', (user_id,)).fetchone()
        
        if not user:
            print("User not found.")
        else:
            # Check if user has sales
            sales = conn.execute('SELECT COUNT(*) FROM sales WHERE user_id = ?', (user_id,)).fetchone()[0]
            if sales > 0:
                print(f"Cannot delete user '{user['username']}' because they have {sales} associated sales.")
            else:
                confirm = input(f"Are you sure you want to delete '{user['username']}'? (y/n): ").lower()
                if confirm == 'y':
                    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
                    conn.commit()
                    print("User deleted successfully!")
                else:
                    print("Deletion canceled.")
        
        conn.close()
    except ValueError:
        print("Error: Invalid user ID.")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    input("\nPress Enter to continue...")

def backup_database():
    clear_screen()
    print("╔════════════════════════════════════════╗")
    print("║          BACKUP DATABASE            ║")
    print("╚════════════════════════════════════════╝")
    
    backup_file = input("\nEnter backup filename (e.g., pos_backup.db): ")
    if not backup_file:
        print("Backup canceled.")
        input("\nPress Enter to continue...")
        return
    
    try:
        import shutil
        shutil.copy2('pos_database.db', backup_file)
        print(f"\nDatabase backed up successfully to {backup_file}")
    except Exception as e:
        print(f"Error during backup: {str(e)}")
    
    input("\nPress Enter to continue...")

def restore_database():
    clear_screen()
    print("╔════════════════════════════════════════╗")
    print("║         RESTORE DATABASE            ║")
    print("╚════════════════════════════════════════╝")
    
    backup_file = input("\nEnter backup filename to restore from: ")
    if not backup_file or not os.path.exists(backup_file):
        print("Backup file not found.")
        input("\nPress Enter to continue...")
        return
    
    confirm = input("\nWARNING: This will overwrite the current database!\nAre you sure? (y/n): ").lower()
    if confirm != 'y':
        print("Restore canceled.")
        input("\nPress Enter to continue...")
        return
    
    try:
        import shutil
        shutil.copy2(backup_file, 'pos_database.db')
        print("\nDatabase restored successfully!")
    except Exception as e:
        print(f"Error during restore: {str(e)}")
    
    input("\nPress Enter to continue...")

# Main function
def main():
    init_db()
    user = login()
    main_menu(user)

if __name__ == "__main__":
    main()
