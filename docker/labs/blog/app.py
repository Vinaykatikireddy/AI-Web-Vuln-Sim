import templates
from flask import Flask, request, jsonify, redirect, url_for, render_template_string
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
def db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Route for homepage with blog posts
@app.route('/')
def home():
    conn = db()
    posts = conn.execute("SELECT * FROM posts ORDER BY created_at DESC").fetchall()
    conn.close()

    return render_template_string(templates.INDEX_PAGE, posts=posts)

# Route for creating a new post (vulnerable to XSS)
@app.route('/create', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        author = request.form.get('author', 'anonymous')

        # Stored XSS vulnerability: No sanitization
        conn = db()
        conn.execute("INSERT INTO posts (title, content, author) VALUES (?, ?, ?)", (title, content, author))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))

    return render_template_string(templates.CREATE_POST_PAGE)

# Route for viewing a specific post
@app.route('/post/<int:post_id>')
def view_post(post_id):
    conn = db()
    c = conn.cursor()

    # Get the post
    c.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
    post = c.fetchone()

    if not post:
        return "Post not found", 404

    # Get comments for the post
    c.execute("SELECT * FROM comments WHERE post_id = ? ORDER BY created_at ASC", (post_id,))
    comments = c.fetchall()
    conn.close()

    # Reflected XSS vulnerability: The comment is included directly in the page without sanitization
    # Any comment with JavaScript will execute when the page loads

    return render_template_string(templates.POST_PAGE, post=post, comments=comments)

# Route for adding a comment
@app.route('/post/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    author = request.form.get('author')
    content = request.form.get('content')

    # Stored XSS vulnerability: No sanitization
    conn = db()
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
    conn = db()
    c = conn.cursor()

    # This is vulnerable to reflected XSS
    # The query parameter directly appears in the HTML without encoding
    c.execute("SELECT * FROM posts WHERE title LIKE ? OR content LIKE ?",
              (f'%{query}%', f'%{query}%'))
    results = c.fetchall()
    conn.close()

    return render_template_string(templates.SEARCH_PAGE, query=query, results=results)

# Health check endpoint
@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    # Initialize database
    init_db()

    # Run application
    app.run(host='0.0.0.0', port=5000, debug=False)