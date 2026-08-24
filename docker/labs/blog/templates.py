SEARCH_PAGE = """
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

INDEX_PAGE = """
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
            <div class="post-content">{{ post['content']|safe }}</div>
            <a href="/post/{{ post['id'] }}">Read more</a>
        </div>
        {% endfor %}

    </div>
</body>
</html>
"""

CREATE_POST_PAGE = """
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

POST_PAGE = """
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
        <div class="post-content">{{ post['content']|safe }}</div>

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