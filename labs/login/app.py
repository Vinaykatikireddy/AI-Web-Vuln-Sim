from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
import bcrypt
import sqlite3
import os
import templates

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
def db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Route for login page
@app.route('/')
def login_page():
    return render_template_string(templates.LOGIN_PAGE)

# Route for login attempt
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    # Log attempt
    conn = db()
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

    return render_template_string(templates.LOGIN_PAGE, error='Invalid username or password')

# Dashboard route (requires authentication)
@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))

    # Vulnerable direct SQL query
    conn = db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = '" + session['username'] + "'")
    user = c.fetchone()

    return render_template_string(templates.DASHBOARD_PAGE, user=user)

# Health check endpoint
@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

# Admin endpoint with SQL injection vulnerability
@app.route('/admin')
def admin():
    # Vulnerable endpoint that allows SQL injection
    query_param = request.args.get('query', '')

    conn = db()
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
    conn = db()
    c = conn.cursor()

    # Vulnerable endpoint
    query = "SELECT * FROM users WHERE username = 'admin' AND password_hash LIKE '%2a%'",

    return jsonify({"status": "vulnerable", "query": query})

# Static routes for CSS and JS
@app.route('/static/<path:filename>')
def static_files(filename):
    return app.send_static_file(filename)

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