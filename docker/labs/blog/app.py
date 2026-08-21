from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Database configuration
DATABASE = 'blog.db'

# Initialize database
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # Create posts table
    c.execute('''CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        author TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    # Create comments table
    c.execute('''CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER,
        author TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (post_id) REFERENCES posts (id)
    )''')

    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    # Insert test data
    # Post with stored XSS vulnerability
    c.execute("INSERT OR IGNORE INTO posts (title, content, author) VALUES (?, ?, ?)",
              ('Welcome to Our Blog', 'Hello world! <script>alert("XSS");</script> This is a demo blog.', 'admin'))

    # Post with reflected XSS vulnerability
    c.execute("INSERT OR IGNORE INTO posts (title, content, author) VALUES (?, ?, ?)",
              ('Reflections', 'Welcome back, <script>alert("Reflected XSS");</script>', 'admin'))

    conn.commit()
    conn.close()

# Database connection helper
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Route for homepage with blog posts
@app.route('/')
def home():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM posts ORDER BY created_at DESC")
    posts = c.fetchall()
    return render_template('index.html', posts=posts)

# Route for creating a new post (vulnerable to XSS)
@app.route('/create', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        author = request.form.get('author', 'anonymous')

        # Stored XSS vulnerability: No sanitization
        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO posts (title, content, author) VALUES (?, ?, ?)", (title, content, author))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))

    return render_template('create-post.html')

# Route for viewing a specific post
@app.route('/post/<int:post_id>')
def view_post(post_id):
    conn = get_db()
    c = conn.cursor()

    # Get the post
    c.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
    post = c.fetchone()

    if not post:
        return "Post not found", 404

    # Get comments for the post
    c.execute("SELECT * FROM comments WHERE post_id = ? ORDER BY created_at ASC", (post_id,))
    comments = c.fetchall()

    # Reflected XSS vulnerability: The comment is included directly in the page without sanitization
    # Any comment with JavaScript will execute when the page loads

    return render_template('post.html', post=post, comments=comments)

# Route for adding a comment
@app.route('/post/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    author = request.form.get('author')
    content = request.form.get('content')

    # Stored XSS vulnerability: No sanitization
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO comments (post_id, author, content) VALUES (?, ?, ?)", (post_id, author, content))
    conn.commit()
    conn.close()

    return redirect(url_for('view_post', post_id=post_id))

# Search endpoint with reflected XSS vulnerability
@app.route('/search')
def search():
    query = request.args.get('q', '')

    # Reflected XSS vulnerability: The search query is reflected in the response without sanitization
    conn = get_db()
    c = conn.cursor()

    # This is vulnerable to reflected XSS
    # The query parameter directly appears in the HTML without encoding
    c.execute("SELECT * FROM posts WHERE title LIKE ? OR content LIKE ?",
              (f'%{query}%', f'%{query}%'))
    results = c.fetchall()

    return render_template('search.html', query=query, results=results)

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
    <title>Blog</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }
        .container { max-width: 800px; margin: 50px auto; background: white; padding: 20px; border-radius: 5px; }
        h1 { color: #333; }
        .post { border-bottom: 1px solid #eee; padding: 20px 0; }
        .post-title { color: #333; margin-bottom: 10px; }
        .post-meta { color: #777; font-size: 0.9em; margin-bottom: 15px; }
        .post-content { line-height: 1.6; }
        .create-link { background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 3px; cursor: pointer; }
        .create-link:hover { background-color: #45a049; }
        .vulnerability { background-color: #fff0f0; border-left: 4px solid #ff6b6b; padding: 10px; margin: 15px 0; }
        .vulnerability h3 { color: #d32f2f; margin: 0 0 10px 0; }
        .vulnerability pre { background-color: #f1f1f1; padding: 10px; border-radius: 3px; overflow-x: auto; }
        .search-box { padding: 10px; width: 70%; margin-right: 10px; }
        .search-button { padding: 10px 20px; background-color: #4CAF50; color: white; border: none; border-radius: 3px; cursor: pointer; }
        .search-button:hover { background-color: #45a049; }
        .search-results { margin-top: 20px; }
        .search-title { font-size: 1.2em; margin-bottom: 10px; }
        .search-item { margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Blog</h1>

        <div class="vulnerability">
            <h3>Security Vulnerability: Stored XSS</h3>
            <p>This blog is vulnerable to stored XSS attacks. Try entering:</p>
            <pre>&lt;script&gt;alert('Stored XSS');&lt;/script&gt;</pre>
            <p>in the title or content field when creating a new post.</p>
        </div>

        <div class="vulnerability">
            <h3>Security Vulnerability: Reflected XSS</h3>
            <p>This blog is vulnerable to reflected XSS attacks. Try entering:</p>
            <pre>&lt;script&gt;alert('Reflected XSS');&lt;/script&gt;</pre>
            <p>in the search box below.</p>
        </div>

        <form action="/search" method="GET" style="margin: 20px 0;">
            <input type="text" class="search-box" name="q" placeholder="Search blog posts..." value="">
            <button type="submit" class="search-button">Search</button>
        </form>

        <a href="/create" class="create-link">Create New Post</a>

        {% for post in posts %}
        <div class="post">
            <h2 class="post-title">{{ post['title'] }}</h2>
            <div class="post-meta">By {{ post['author'] }} on {{ post['created_at'] }}</div>
            <div class="post-content">{{ post['content'] }}</div>
            <a href="/post/{{ post['id'] }}">Read more</a>
        </div>
        {% endfor %}

    </div>
</body>
</html>
    """
    with open('templates/index.html', 'w') as f:
        f.write(index_template)

if not os.path.exists('templates/create-post.html'):
    create_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Create Post</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }
        .container { max-width: 800px; margin: 50px auto; background: white; padding: 20px; border-radius: 5px; }
        h1 { color: #333; }
        input[type=text], textarea { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 3px; }
        textarea { height: 200px; }
        button { background-color: #4CAF50; color: white; padding: 10px 15px; border: none; border-radius: 3px; cursor: pointer; }
        button:hover { background-color: #45a049; }
        .back-link { color: #4CAF50; text-decoration: none; }
        .vulnerability { background-color: #fff0f0; border-left: 4px solid #ff6b6b; padding: 10px; margin: 15px 0; }
        .vulnerability h3 { color: #d32f2f; margin: 0 0 10px 0; }
        .vulnerability pre { background-color: #f1f1f1; padding: 10px; border-radius: 3px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Create New Post</h1>

        <div class="vulnerability">
            <h3>Security Vulnerability: Stored XSS</h3>
            <p>This form is vulnerable to stored XSS attacks. You can insert JavaScript code in the title or content fields:</p>
            <pre>&lt;script&gt;alert('XSS');&lt;/script&gt;</pre>
            <p>When another user views this post, the code will execute!</p>
        </div>

        <form method="POST" action="/create">
            <input type="text" name="title" placeholder="Title" required>
            <textarea name="content" placeholder="Content" required></textarea>
            <input type="text" name="author" placeholder="Author (optional)" value="anonymous">
            <button type="submit">Create Post</button>
        </form>

        <a href="/" class="back-link">← Back to Blog</a>
    </div>
</body>
</html>
    """
    with open('templates/create-post.html', 'w') as f:
        f.write(create_template)

if not os.path.exists('templates/post.html'):
    post_template = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ post['title'] }} - Blog</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }
        .container { max-width: 800px; margin: 50px auto; background: white; padding: 20px; border-radius: 5px; }
        h1 { color: #333; }
        .post-title { color: #333; margin-bottom: 10px; }
        .post-meta { color: #777; font-size: 0.9em; margin-bottom: 15px; }
        .post-content { line-height: 1.6; }
        .comment { border-bottom: 1px solid #eee; padding: 15px 0; }
        .comment-author { color: #4CAF50; font-weight: bold; }
        .comment-content { margin-top: 5px; }
        .comment-form { margin-top: 20px; }
        input[type=text] { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 3px; }
        button { background-color: #4CAF50; color: white; padding: 10px 15px; border: none; border-radius: 3px; cursor: pointer; }
        button:hover { background-color: #45a049; }
        .back-link { color: #4CAF50; text-decoration: none; }
        .vulnerability { background-color: #fff0f0; border-left: 4px solid #ff6b6b; padding: 10px; margin: 15px 0; }
        .vulnerability h3 { color: #d32f2f; margin: 0 0 10px 0; }
        .vulnerability pre { background-color: #f1f1f1; padding: 10px; border-radius: 3px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="post-title">{{ post['title'] }}</h1>
        <div class="post-meta">By {{ post['author'] }} on {{ post['created_at'] }}</div>
        <div class="post-content">{{ post['content'] }}</div>

        <div class="vulnerability">
            <h3>Security Vulnerability: Stored XSS</h3>
            <p>This post is vulnerable to stored XSS attacks. Try adding a comment with:</p>
            <pre>&lt;script&gt;alert('XSS in comment');&lt;/script&gt;</pre>
            <p>When you submit, this JavaScript will be stored and executed when anyone views the post!</p>
        </div>

        <h2>Comments</h2>
        {% for comment in comments %}
        <div class="comment">
            <div class="comment-author">{{ comment['author'] }}</div>
            <div class="comment-content">{{ comment['content'] }}</div>
        </div>
        {% endfor %}

        <h3>Add a Comment</h3>
        <form method="POST" action="/post/{{ post['id'] }}/comment" class="comment-form">
            <input type="text" name="author" placeholder="Your Name" required>
            <textarea name="content" placeholder="Your comment" required></textarea>
            <button type="submit">Add Comment</button>
        </form>

        <a href="/" class="back-link">← Back to Blog</a>
    </div>
</body>
</html>
    """
    with open('templates/post.html', 'w') as f:
        f.write(post_template)

if not os.path.exists('templates/search.html'):
    search_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Search Results</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }
        .container { max-width: 800px; margin: 50px auto; background: white; padding: 20px; border-radius: 5px; }
        h1 { color: #333; }
        .search-query { color: #4CAF50; }
        .search-result { border-bottom: 1px solid #eee; padding: 20px 0; }
        .result-title { color: #333; margin-bottom: 10px; }
        .result-meta { color: #777; font-size: 0.9em; margin-bottom: 15px; }
        .result-content { line-height: 1.6; }
        .back-link { color: #4CAF50; text-decoration: none; }
        .vulnerability { background-color: #fff0f0; border-left: 4px solid #ff6b6b; padding: 10px; margin: 15px 0; }
        .vulnerability h3 { color: #d32f2f; margin: 0 0 10px 0; }
        .vulnerability pre { background-color: #f1f1f1; padding: 10px; border-radius: 3px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Search Results for "<span class="search-query">{{ query }}</span>"</h1>

        <div class="vulnerability">
            <h3>Security Vulnerability: Reflected XSS</h3>
            <p>This search page is vulnerable to reflected XSS attacks. The search query is included directly in the page without encoding.</p>
            <p>Try entering this in the search box:</p>
            <pre>&lt;script&gt;alert('Reflected XSS');&lt;/script&gt;</pre>
            <p>Note: The exact text you search for will appear on this page, making it vulnerable to reflected XSS.</p>
        </div>

        {% if results %}
        <h2>Results</h2>
        {% for result in results %}
        <div class="search-result">
            <h3 class="result-title">{{ result['title'] }}</h3>
            <div class="result-meta">By {{ result['author'] }} on {{ result['created_at'] }}</div>
            <div class="result-content">{{ result['content'] }}</div>
            <a href="/post/{{ result['id'] }}">View Post</a>
        </div>
        {% endfor %}
        {% else %}
        <p>No results found for "{{ query }}".</p>
        {% endif %}

        <a href="/" class="back-link">← Back to Blog</a>
    </div>
</body>
</html>
    """
    with open('templates/search.html', 'w') as f:
        f.write(search_template)

# Health check endpoint
@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    # Initialize database
    init_db()

    # Run application
    app.run(host='0.0.0.0', port=5000, debug=False)