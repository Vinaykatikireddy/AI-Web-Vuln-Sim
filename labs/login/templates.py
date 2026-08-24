LOGIN_PAGE = """
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

DASHBOARD_PAGE = """
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