from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import bcrypt
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Database configuration
DATABASE = 'login.db'

# Initialize database
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    # Create logs table
    c.execute('''CREATE TABLE IF NOT EXISTS login_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        success BOOLEAN,
        ip_address TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    # Insert test user (vulnerable password)
    test_password = 'password123'
    hashed = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt())

    c.execute("INSERT OR IGNORE INTO users (username, password_hash) VALUES (?, ?)",
              ('admin', hashed))

    conn.commit()
    conn.close()

# Database connection helper
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Route for login page
@app.route('/')
def login_page():
    return render_template('login.html')

# Route for login attempt
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    # Log attempt
    conn = get_db()
    c = conn.cursor()

    # SQL Injection vulnerability: No parameterized query
    # Vulnerable query: Direct string concatenation
    query = f"SELECT * FROM users WHERE username = '{username}'"
    c.execute(query)

    user = c.fetchone()

    success = False

    if user:
        # Password validation vulnerability: Using direct comparison
        # This creates a timing attack vulnerability
        stored_password = user['password_hash']

        # This is a hardcoded password check for demonstration
        # In a real app, this should use bcrypt for secure comparison
        # But for vulnerable app, we allow simple verification
        if password == 'password123':  # Vulnerable comparison
            success = True
            session['logged_in'] = True
            session['username'] = username

            # Log successful login
            c.execute("INSERT INTO login_attempts (username, success, ip_address) VALUES (?, ?, ?)",
                     (username, True, request.remote_addr))
            conn.commit()

            return redirect(url_for('dashboard'))

    # Log failed attempt
    c.execute("INSERT INTO login_attempts (username, success, ip_address) VALUES (?, ?, ?)",
              (username, False, request.remote_addr))
    conn.commit()

    return render_template('login.html', error='Invalid username or password')

# Dashboard route (requires authentication)
@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))

    # Vulnerable direct SQL query
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = '" + session['username'] + "'")
    user = c.fetchone()

    return render_template('dashboard.html', user=user)

# Health check endpoint
@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

# Admin endpoint with SQL injection vulnerability
@app.route('/admin')
def admin():
    # Vulnerable endpoint that allows SQL injection
    query_param = request.args.get('query', '')

    conn = get_db()
    c = conn.cursor()

    # SQL Injection vulnerability - direct string concatenation
    query = f"SELECT * FROM users WHERE username LIKE '%{query_param}%'"

    try:
        c.execute(query)
        results = c.fetchall()

        if len(results) > 0:
            return jsonify([dict(row) for row in results])
        else:
            return jsonify([])
    except Exception as e:
        return jsonify({"error": str(e)})

# Test endpoint for SQL injection
@app.route('/test-sql')
def test_sql():
    conn = get_db()
    c = conn.cursor()

    # Vulnerable endpoint
    query = "SELECT * FROM users WHERE username = 'admin' AND password_hash LIKE '%2a%'",

    return jsonify({"status": "vulnerable", "query": query})

# Static routes for CSS and JS
@app.route('/static/<path:filename>')
def static_files(filename):
    return app.send_static_file(filename)

# Create templates directory if it doesn't exist
os.makedirs('templates', exist_ok=True)

# Create template files
if not os.path.exists('templates/login.html'):
    login_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }
        .container { max-width: 400px; margin: 50px auto; background: white; padding: 20px; border-radius: 5px; }
        h2 { text-align: center; color: #333; }
        input[type=text], input[type=password] { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 3px; }
        button { background-color: #4CAF50; color: white; padding: 10px 15px; border: none; border-radius: 3px; cursor: pointer; width: 100%; }
        button:hover { background-color: #45a049; }
        .error { color: red; text-align: center; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Login</h2>
        {% if error %}
            <div class="error">{{ error }}</div>
        {% endif %}
        <form method="POST" action="/login">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
    </div>
</body>
</html>
    """
    with open('templates/login.html', 'w') as f:
        f.write(login_template)

if not os.path.exists('templates/dashboard.html'):
    dashboard_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }
        .container { max-width: 800px; margin: 50px auto; background: white; padding: 20px; border-radius: 5px; }
        h2 { color: #333; }
        .user-info { background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .vulnerability { background-color: #fff0f0; border-left: 4px solid #ff6b6b; padding: 10px; margin: 15px 0; }
        .vulnerability h3 { color: #d32f2f; margin: 0 0 10px 0; }
        .vulnerability pre { background-color: #f1f1f1; padding: 10px; border-radius: 3px; overflow-x: auto; }
        .admin-link { color: #ff6b6b; text-decoration: none; }
        .admin-link:hover { text-decoration: underline; }
        .logout { background-color: #f44336; color: white; padding: 8px 15px; border: none; border-radius: 3px; cursor: pointer; margin-top: 20px; }
        .logout:hover { background-color: #d32f2f; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Welcome to the Dashboard, {{ user['username'] }}!</h2>

        <div class="user-info">
            <p><strong>Username:</strong> {{ user['username'] }}</p>
            <p><strong>Created:</strong> {{ user['created_at'] }}</p>
        </div>

        <div class="vulnerability">
            <h3>Security Vulnerability: SQL Injection</h3>
            <p>This application is deliberately vulnerable to SQL injection attacks. Try entering:</p>
            <pre>' OR 1=1--</pre>
            <p>in the login form to bypass authentication.</p>
        </div>

        <div class="vulnerability">
            <h3>Security Vulnerability: Weak Authentication</h3>
            <p>The username 'admin' has a weak password 'password123'. This is intentional for demonstration purposes.</p>
        </div>

        <div class="vulnerability">
            <h3>Security Vulnerability: Direct SQL Queries</h3>
            <p>Click <a href="/admin?query=admin" class="admin-link">here</a> to test SQL injection via the admin endpoint. Try different queries like:</p>
            <pre>' OR 'a'='a</pre>
            <pre>' UNION SELECT * FROM users--</pre>
        </div>

        <button class="logout" onclick="location.href='/logout'">Logout</button>
    </div>

    <script>
        function logout() {
            window.location.href = '/logout';
        }
    </script>
</body>
</html>
    """
    with open('templates/dashboard.html', 'w') as f:
        f.write(dashboard_template)

# Create logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    # Initialize database
    init_db()

    # Run application
    app.run(host='0.0.0.0', port=5000, debug=False)