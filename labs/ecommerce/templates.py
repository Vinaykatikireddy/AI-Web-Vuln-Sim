HOME_PAGE = """
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

PRODUCT_PAGE = """
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

CART_PAGE = """
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

CHECKOUT_PAGE = """
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

ORDERS_PAGE = """
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

ADMIN_PAGE = """
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