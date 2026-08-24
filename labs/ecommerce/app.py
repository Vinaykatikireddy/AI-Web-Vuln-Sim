from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session
import sqlite3
import os
from dotenv import load_dotenv
import templates

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Database configuration
DATABASE = 'ecommerce.db'

# Initialize database
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # Create products table
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        inventory INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT,
        email TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    # Create orders table
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        total_price REAL,
        status TEXT DEFAULT 'pending',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (product_id) REFERENCES products (id)
    )''')

    # Insert test data
    # Products with IDOR vulnerability
    c.execute("INSERT OR IGNORE INTO products (name, description, price, inventory) VALUES (?, ?, ?, ?)",
              ('Laptop', 'High-performance laptop for professionals', 999.99, 10))
    c.execute("INSERT OR IGNORE INTO products (name, description, price, inventory) VALUES (?, ?, ?, ?)",
              ('Smartphone', 'Latest model smartphone with advanced features', 699.99, 20))
    c.execute("INSERT OR IGNORE INTO products (name, description, price, inventory) VALUES (?, ?, ?, ?)",
              ('Tablet', 'Portable tablet for browsing and media', 399.99, 15))

    # Add a test user
    c.execute("INSERT OR IGNORE INTO users (username, email) VALUES (?, ?)",
              ('guest', 'guest@example.com'))

    conn.commit()
    conn.close()

# Database connection helper
def db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Route for homepage with products
@app.route('/')
def home():
    conn = db()
    products = conn.execute("SELECT * FROM products WHERE inventory > 0 ORDER BY name").fetchall()
    conn.close()
    return render_template_string(templates.HOME_PAGE, products=products)

# Route for product details
@app.route('/product/<int:product_id>')
def product_details(product_id):
    conn = db()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    conn.close()

    if not product:
        return "Product not found", 404

    return render_template_string(templates.PRODUCT_PAGE, product=product)

# Route for adding to cart
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.form.get('product_id')
    quantity = request.form.get('quantity', 1)

    # IDOR vulnerability - User can change any product's ID in the URL
    # This allows users to access products they shouldn't have access to

    # We're not checking if the user is authenticated or has permission
    # Any user can access any product id

    conn = db()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    conn.close()

    if not product:
        return "Product not found", 404

    # Add to cart (in session for demo)
    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append({
        'product_id': product_id,
        'quantity': quantity,
        'name': product['name'],
        'price': product['price']
    })

    return redirect(url_for('cart'))

# Route for cart
@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    return render_template_string(templates.CART_PAGE, cart_items=cart_items)

# Route for checkout
@app.route('/checkout', methods=['POST'])
def checkout():
    cart_items = session.get('cart', [])

    if not cart_items:
        return redirect(url_for('home'))

    # IDOR vulnerability - User can manipulate the user_id parameter
    # This allows users to place orders on behalf of other users

    # In a secure system, we would use the authenticated user's ID
    # But here we're using what's passed in, creating an IDOR vulnerability
    user_id = request.form.get('user_id', 1)  # Vulnerable - User can change this

    if not user_id:
        return "Invalid user", 400

    # Create order
    conn = db()
    c = conn.cursor()

    total_price = 0
    for item in cart_items:
        # We're not checking if the user has permission to buy this item
        # This creates an IDOR vulnerability
        c.execute("SELECT price FROM products WHERE id = ?", (item['product_id'],))
        product_price = c.fetchone()

        if product_price:
            item_price = float(product_price[0])
            item_quantity = int(item['quantity'])
            item_total = item_price * item_quantity
            total_price += item_total

            # Store the order
            c.execute("INSERT INTO orders (user_id, product_id, quantity, total_price) VALUES (?, ?, ?, ?)",
                     (user_id, item['product_id'], item_quantity, item_total))

    conn.commit()
    conn.close()

    # Clear cart
    session['cart'] = []

    return render_template_string(templates.CHECKOUT_PAGE, total_price=total_price)

# Route for order history
@app.route('/orders')
def orders():
    # IDOR vulnerability - User can change the user_id in the URL
    user_id = request.args.get('user_id', session.get('user_id', 1))

    conn = db()
    orders = conn.execute("SELECT o.*, p.name, p.price FROM orders o JOIN products p ON o.product_id = p.id WHERE o.user_id = ? ORDER BY o.created_at DESC", (user_id,)).fetchall()
    conn.close()

    # The vulnerability here is that a user can view orders of other users
    # by changing the user_id parameter in the URL

    return render_template_string(templates.ORDERS_PAGE, orders=orders, current_user_id=user_id)

# Route for admin panel
@app.route('/admin')
def admin():
    # IDOR vulnerability - Only users with admin privileges should access this
    # But we're not checking any permissions

    conn = db()
    users = conn.execute("SELECT * FROM users").fetchall()

    recent_orders = conn.execute("SELECT * FROM orders ORDER BY created_at DESC LIMIT 10").fetchall()
    conn.close()

    return render_template_string(templates.ADMIN_PAGE, users=users, recent_orders=recent_orders)

# Health check endpoint
@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

# Initialize database
init_db()

if __name__ == '__main__':
    # Run application
    app.run(host='0.0.0.0', port=5000, debug=False)