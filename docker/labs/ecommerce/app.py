from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import sqlite3
import os
from dotenv import load_dotenv

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
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Route for homepage with products
@app.route('/')
def home():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE inventory > 0 ORDER BY name")
    products = c.fetchall()
    return render_template('index.html', products=products)

# Route for product details
@app.route('/product/<int:product_id>')
def product_details(product_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = c.fetchone()

    if not product:
        return "Product not found", 404

    return render_template('product.html', product=product)

# Route for adding to cart
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.form.get('product_id')
    quantity = request.form.get('quantity', 1)

    # IDOR vulnerability - User can change any product's ID in the URL
    # This allows users to access products they shouldn't have access to

    # We're not checking if the user is authenticated or has permission
    # Any user can access any product id

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = c.fetchone()

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
    return render_template('cart.html', cart_items=cart_items)

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
    conn = get_db()
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

    # Clear cart
    session['cart'] = []

    return render_template('checkout_success.html', total_price=total_price)

# Route for order history
@app.route('/orders')
def orders():
    # IDOR vulnerability - User can change the user_id in the URL
    user_id = request.args.get('user_id', session.get('user_id', 1))

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT o.*, p.name, p.price FROM orders o JOIN products p ON o.product_id = p.id WHERE o.user_id = ? ORDER BY o.created_at DESC", (user_id,))
    orders = c.fetchall()

    # The vulnerability here is that a user can view orders of other users
    # by changing the user_id parameter in the URL

    return render_template('orders.html', orders=orders, current_user_id=user_id)

# Route for admin panel
@app.route('/admin')
def admin():
    # IDOR vulnerability - Only users with admin privileges should access this
    # But we're not checking any permissions

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    users = c.fetchall()

    c.execute("SELECT * FROM orders ORDER BY created_at DESC LIMIT 10")
    recent_orders = c.fetchall()

    return render_template('admin.html', users=users, recent_orders=recent_orders)

# Health check endpoint
@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

# Create templates directory if it doesn't exist
os.makedirs('templates', exist_ok=True)

# Create template files if they don't exist
if not os.path.exists('templates/index.html'):
    index_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Ecommerce Store</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }
        .container { max-width: 1200px; margin: 50px auto; background: white; padding: 20px; border-radius: 5px; }
        h1 { color: #333; }
        .products { display: flex; flex-wrap: wrap; gap: 20px; }
        .product { border: 1px solid #eee; border-radius: 5px; padding: 15px; width: calc(33.333% - 20px); box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .product h2 { color: #333; margin-bottom: 10px; }
        .product p { color: #666; }
        .product .price { color: #4CAF50; font-weight: bold; }
        .product button { background-color: #4CAF50; color: white; padding: 10px 15px; border: none; border-radius: 3px; cursor: pointer; }
        .product button:hover { background-color: #45a049; }
        .cart-link { background-color: #2196F3; color: white; padding: 10px 20px; border: none; border-radius: 3px; cursor: pointer; }
        .cart-link:hover { background-color: #0b7dda; }
        .vulnerability { background-color: #fff0f0; border-left: 4px solid #ff6b6b; padding: 10px; margin: 15px 0; }
        .vulnerability h3 { color: #d32f2f; margin: 0 0 10px 0; }
        .vulnerability pre { background-color: #f1f1f1; padding: 10px; border-radius: 3px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Ecommerce Store</h1>

        <div class="vulnerability">
            <h3>Security Vulnerability: IDOR (Insecure Direct Object Reference)</h3>
            <p>This application is vulnerable to IDOR attacks. Test the following:</p>
            <ol>
                <li>Change <code>product_id</code> in the URL to access other products</li>
                <li>Try changing <code>user_id</code> in the checkout form to place orders under different accounts</li>
                <li>Access <a href="/orders?user_id=1">/orders?user_id=1</a> and change the user_id to view other user's orders</li>
                <li>Access the <a href="/admin">admin panel</a> without authentication</li>
            </ol>
        </div>

        <div class="products">
            {% for product in products %}
            <div class="product">
                <h2>{{ product['name'] }}</h2>
                <p>{{ product['description'] }}</p>
                <p class="price">$ {{ product['price'] }}</p>
                <form method="POST" action="/add_to_cart">
                    <input type="hidden" name="product_id" value="{{ product['id'] }}">
                    <button type="submit">Add to Cart</button>
                </form>
            </div>
            {% endfor %}
        </div>

        <a href="/cart" class="cart-link">View Cart</a>
    </div>
</body>
</html>
    """
    with open('templates/index.html', 'w') as f:
        f.write(index_template)

if not os.path.exists('templates/product.html'):
    product_template = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ product['name'] }} - Ecommerce Store</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }
        .container { max-width: 800px; margin: 50px auto; background: white; padding: 20px; border-radius: 5px; }
        h1 { color: #333; }
        .product-info h1 { margin-bottom: 10px; }
        .product-info p { color: #666; }
        .product-info .price { color: #4CAF50; font-weight: bold; font-size: 1.5em; }
        .add-to-cart button { background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 3px; cursor: pointer; }
        .add-to-cart button:hover { background-color: #45a049; }
        .back-link { color: #4CAF50; text-decoration: none; }
        .vulnerability { background-color: #fff0f0; border-left: 4px solid #ff6b6b; padding: 10px; margin: 15px 0; }
        .vulnerability h3 { color: #d32f2f; margin: 0 0 10px 0; }
        .vulnerability pre { background-color: #f1f1f1; padding: 10px; border-radius: 3px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="container">
        <div class="product-info">
            <h1>{{ product['name'] }}</h1>
            <p>{{ product['description'] }}</p>
            <p class="price">$ {{ product['price'] }}</p>
            <p>Inventory: {{ product['inventory'] }}</p>

            <div class="add-to-cart">
                <form method="POST" action="/add_to_cart">
                    <input type="hidden" name="product_id" value="{{ product['id'] }}">
                    <button type="submit">Add to Cart</button>
                </form>
            </div>
        </div>

        <div class="vulnerability">
            <h3>Security Vulnerability: IDOR (Insecure Direct Object Reference)</h3>
            <p>This product page is vulnerable to IDOR attacks. You can access other products by changing the product_id in the URL.</p>
            <p>Try accessing <code>/product/1</code>, <code>/product/2</code>, <code>/product/3</code> etc.</p>
        </div>

        <a href="/" class="back-link">← Back to Store</a>
    </div>
</body>
</html>
    """
    with open('templates/product.html', 'w') as f:
        f.write(product_template)

if not os.path.exists('templates/cart.html'):
    cart_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Cart - Ecommerce Store</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }
        .container { max-width: 800px; margin: 50px auto; background: white; padding: 20px; border-radius: 5px; }
        h1 { color: #333; }
        .cart-item { border-bottom: 1px solid #eee; padding: 15px 0; }
        .cart-item h3 { color: #333; margin-bottom: 5px; }
        .cart-item p { color: #666; }
        .cart-item .price { color: #4CAF50; font-weight: bold; }
        .cart-item .quantity { color: #666; }
        .checkout-btn { background-color: #4CAF50; color: white; padding: 12px 20px; border: none; border-radius: 3px; cursor: pointer; }
        .checkout-btn:hover { background-color: #45a049; }
        .back-link { color: #4CAF50; text-decoration: none; }
        .vulnerability { background-color: #fff0f0; border-left: 4px solid #ff6b6b; padding: 10px; margin: 15px 0; }
        .vulnerability h3 { color: #d32f2f; margin: 0 0 10px 0; }
        .vulnerability pre { background-color: #f1f1f1; padding: 10px; border-radius: 3px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Shopping Cart</h1>

        {% if cart_items %}
        {% for item in cart_items %}
        <div class="cart-item">
            <h3>{{ item['name'] }}</h3>
            <p>Price: $ {{ item['price'] }}</p>
            <p class="quantity">Quantity: {{ item['quantity'] }}</p>
            <p class="price">Subtotal: $ {{ item['price'] * item['quantity'] }}</p>
        </div>
        {% endfor %}

        <div class="vulnerability">
            <h3>Security Vulnerability: IDOR (Insecure Direct Object Reference)</h3>
            <p>This checkout form is vulnerable to IDOR attacks. Try modifying the user_id field to place an order as another user.</p>
            <pre>
&lt;form method="POST" action="/checkout"&gt;
    &lt;input type="hidden" name="user_id" value="1"&gt;
    &lt;!-- Change the value from 1 to 2, 3, etc. to see the vulnerability --&gt;
    &lt;button type="submit" class="checkout-btn"&gt;Checkout&lt;/button&gt;
&lt;/form&gt;
            </pre>
        </div>

        <form method="POST" action="/checkout">
            <!-- This is the vulnerable parameter -->
            <input type="hidden" name="user_id" value="1">
            <button type="submit" class="checkout-btn">Checkout</button>
        </form>

        {% else %}
        <p>Your cart is empty.</p>
        {% endif %}

        <a href="/" class="back-link">← Back to Store</a>
    </div>
</body>
</html>
    """
    with open('templates/cart.html', 'w') as f:
        f.write(cart_template)

if not os.path.exists('templates/checkout_success.html'):
    checkout_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Order Confirmation - Ecommerce Store</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }
        .container { max-width: 800px; margin: 50px auto; background: white; padding: 20px; border-radius: 5px; }
        h1 { color: #333; }
        .order-summary { background-color: #f9f9f9; padding: 20px; margin: 20px 0; }
        .order-summary h2 { margin-bottom: 10px; }
        .order-summary p { margin: 5px 0; }
        .success-icon { color: #4CAF50; font-size: 50px; margin-bottom: 20px; }
        .back-link { color: #4CAF50; text-decoration: none; }
        .vulnerability { background-color: #fff0f0; border-left: 4px solid #ff6b6b; padding: 10px; margin: 15px 0; }
        .vulnerability h3 { color: #d32f2f; margin: 0 0 10px 0; }
        .vulnerability pre { background-color: #f1f1f1; padding: 10px; border-radius: 3px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="container">
        <div class="success-icon">✓</div>
        <h1>Order Confirmed!</h1>

        <div class="order-summary">
            <h2>Order Summary</h2>
            <p>Total Amount: $ {{ total_price }}</p>
            <p>Thank you for your purchase!</p>
        </div>

        <div class="vulnerability">
            <h3>Security Vulnerability: IDOR (Insecure Direct Object Reference)</h3>
            <p>This order confirmation page could be accessed by any user who knows the correct URL pattern. In a secure system, we would check authorization before displaying this page.</p>
            <p>Try accessing <code>/orders?user_id=1</code> and <code>/orders?user_id=2</code> to see the vulnerability.</p>
        </div>

        <a href="/" class="back-link">← Back to Store</a>
    </div>
</body>
</html>
    """
    with open('templates/checkout_success.html', 'w') as f:
        f.write(checkout_template)

if not os.path.exists('templates/orders.html'):
    orders_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Order History - Ecommerce Store</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }
        .container { max-width: 1000px; margin: 50px auto; background: white; padding: 20px; border-radius: 5px; }
        h1 { color: #333; }
        .order { border-bottom: 1px solid #eee; padding: 15px 0; }
        .order h3 { margin-bottom: 5px; }
        .order p { color: #666; }
        .back-link { color: #4CAF50; text-decoration: none; }
        .vulnerability { background-color: #fff0f0; border-left: 4px solid #ff6b6b; padding: 10px; margin: 15px 0; }
        .vulnerability h3 { color: #d32f2f; margin: 0 0 10px 0; }
        .vulnerability pre { background-color: #f1f1f1; padding: 10px; border-radius: 3px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Order History</h1>

        {% if orders %}
        {% for order in orders %}
        <div class="order">
            <h3>Order #{{ order['id'] }} - $ {{ order['total_price'] }}</h3>
            <p>Product: {{ order['name'] }}</p>
            <p>Quantity: {{ order['quantity'] }}</p>
            <p>Status: {{ order['status'] }}</p>
            <p>Date: {{ order['created_at'] }}</p>
        </div>
        {% endfor %}

        <div class="vulnerability">
            <h3>Security Vulnerability: IDOR (Insecure Direct Object Reference)</h3>
            <p>This page is vulnerable to IDOR attacks. You can view other users' order history by changing the user_id parameter in the URL.</p>
            <p>Try accessing <code>/orders?user_id=1</code>, <code>/orders?user_id=2</code>, <code>/orders?user_id=999</code>, etc.</p>
            <p>Note: In a secure system, you would only see your own orders, not others'</p>
        </div>

        {% else %}
        <p>You have no orders.</p>
        {% endif %}

        <a href="/" class="back-link">← Back to Store</a>
    </div>
</body>
</html>
    """
    with open('templates/orders.html', 'w') as f:
        f.write(orders_template)

if not os.path.exists('templates/admin.html'):
    admin_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Admin Panel - Ecommerce Store</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }
        .container { max-width: 1200px; margin: 50px auto; background: white; padding: 20px; border-radius: 5px; }
        h1 { color: #333; }
        .admin-section { margin-bottom: 30px; }
        h2 { color: #333; border-bottom: 1px solid #eee; padding-bottom: 10px; }
        .users-table, .orders-table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        .users-table th, .users-table td, .orders-table th, .orders-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        .users-table th, .orders-table th { background-color: #f2f2f2; }
        .users-table tr:nth-child(even), .orders-table tr:nth-child(even) { background-color: #f9f9f9; }
        .back-link { color: #4CAF50; text-decoration: none; }
        .vulnerability { background-color: #fff0f0; border-left: 4px solid #ff6b6b; padding: 10px; margin: 15px 0; }
        .vulnerability h3 { color: #d32f2f; margin: 0 0 10px 0; }
        .vulnerability pre { background-color: #f1f1f1; padding: 10px; border-radius: 3px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Admin Panel</h1>

        <div class="admin-section">
            <h2>Users</h2>
            <table class="users-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Username</th>
                        <th>Email</th>
                        <th>Created</th>
                    </tr>
                </thead>
                <tbody>
                    {% for user in users %}
                    <tr>
                        <td>{{ user['id'] }}</td>
                        <td>{{ user['username'] }}</td>
                        <td>{{ user['email'] }}</td>
                        <td>{{ user['created_at'] }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="admin-section">
            <h2>Recent Orders</h2>
            <table class="orders-table">
                <thead>
                    <tr>
                        <th>Order ID</th>
                        <th>User ID</th>
                        <th>Product</th>
                        <th>Quantity</th>
                        <th>Total</th>
                        <th>Status</th>
                        <th>Date</th>
                    </tr>
                </thead>
                <tbody>
                    {% for order in recent_orders %}
                    <tr>
                        <td>{{ order['id'] }}</td>
                        <td>{{ order['user_id'] }}</td>
                        <td>{{ order['name'] }}</td>
                        <td>{{ order['quantity'] }}</td>
                        <td>$ {{ order['total_price'] }}</td>
                        <td>{{ order['status'] }}</td>
                        <td>{{ order['created_at'] }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="vulnerability">
            <h3>Security Vulnerability: IDOR (Insecure Direct Object Reference)</h3>
            <p>This admin panel is accessible to any user without authentication. This is a critical vulnerability! In a secure system:</p>
            <ul>
                <li>Admin panels should be accessible only to authorized administrators</li>
                <li>Authentication and authorization checks should be implemented</li>
                <li>Access control rules should be enforced</li>
            </ul>
            <p>This page should be behind authentication and user roles, not exposed to the public!</p>
        </div>

        <a href="/" class="back-link">← Back to Store</a>
    </div>
</body>
</html>
    """
    with open('templates/admin.html', 'w') as f:
        f.write(admin_template)

# Health check endpoint
@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    # Initialize database
    init_db()

    # Run application
    app.run(host='0.0.0.0', port=5000, debug=False)