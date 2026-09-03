HOME_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>File Upload - Ecommerce Store</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }
        .container { max-width: 800px; margin: 50px auto; background: white; padding: 20px; border-radius: 5px; }
        h1 { color: #333; }
        .upload-link { background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 3px; cursor: pointer; }
        .upload-link:hover { background-color: #45a049; }
        .vulnerability { background-color: #fff0f0; border-left: 4px solid #ff6b6b; padding: 10px; margin: 15px 0; }
        .vulnerability h3 { color: #d32f2f; margin: 0 0 10px 0; }
        .vulnerability pre { background-color: #f1f1f1; padding: 10px; border-radius: 3px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>File Upload Service</h1>

        <div class="vulnerability">
            <h3>Security Vulnerability: Unsafe File Upload</h3>
            <p>This application is vulnerable to unsafe file upload attacks. An attacker can upload malicious files including:</p>
            <ul>
                <li>Web shells (PHP, JSP, ASPX)</li>
                <li>Malicious scripts</li>
                <li>Executable files</li>
            </ul>
            <p>Try uploading a file named "shell.php.jpg" with a PHP shell inside.</p>
            <p>Then access it via <code>/uploads/[filename]</code> to execute the shell.</p>
        </div>

        <a href="/upload" class="upload-link">Upload a File</a>

        <div class="vulnerability">
            <h3>Security Vulnerability: Admin Panel Exposure</h3>
            <p>The admin panel is exposed to everyone without authentication.</p>
            <p>Access the <a href="/admin">admin panel</a> to see all uploaded files.</p>
        </div>
    </div>
</body>
</html>
"""

UPLOAD_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Upload File</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }
        .container { max-width: 800px; margin: 50px auto; background: white; padding: 20px; border-radius: 5px; }
        h1 { color: #333; }
        input[type=file] { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; }
        button { background-color: #4CAF50; color: white; padding: 10px 15px; border: none; border-radius: 3px; cursor: pointer; }
        button:hover { background-color: #45a049; }
        .back-link { color: #4CAF50; text-decoration: none; }
        .vulnerability { background-color: #fff0f0; border-left: 4px solid #ff6b6b; padding: 10px; margin: 15px 0; }
        .vulnerability h3 { color: #d32f2f; margin: 0 0 10px 0; }
        .vulnerability pre { background-color: #f1f1f1; padding: 10px; border-radius: 3px; overflow-x: auto; }
        .error { color: red; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Upload a File</h1>

        <div class="vulnerability">
            <h3>Security Vulnerability: Unsafe File Upload</h3>
            <p>This form is vulnerable to unsafe file upload attacks. The application only checks the file extension, not the actual content. Try uploading:</p>
            <ol>
                <li>A PHP web shell named "shell.php.jpg"</li>
                <li>An executable file named "malware.exe.jpg"</li>
                <li>A JSP file named "shell.jsp.jpg"</li>
            </ol>
            <p>Warning: Files will be executable after upload!</p>
        </div>

        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}

        <form method="POST" enctype="multipart/form-data" action="/upload">
            <input type="file" name="file" required>
            <button type="submit">Upload File</button>
        </form>

        <a href="/" class="back-link">← Back to Home</a>
    </div>
</body>
</html>
"""

SUCCESS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Upload Successful</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }
        .container { max-width: 800px; margin: 50px auto; background: white; padding: 20px; border-radius: 5px; }
        h1 { color: #333; }
        .success-icon { color: #4CAF50; font-size: 50px; margin-bottom: 20px; }
        .file-link { color: #4CAF50; text-decoration: none; }
        .back-link { color: #4CAF50; text-decoration: none; }
        .vulnerability { background-color: #fff0f0; border-left: 4px solid #ff6b6b; padding: 10px; margin: 15px 0; }
        .vulnerability h3 { color: #d32f2f; margin: 0 0 10px 0; }
        .vulnerability pre { background-color: #f1f1f1; padding: 10px; border-radius: 3px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="container">
        <div class="success-icon">✓</div>
        <h1>Upload Successful!</h1>

        <p>Your file has been uploaded successfully.</p>

        <p>File URL: <a href="/uploads/{{ filename }}" class="file-link" target="_blank">/uploads/{{ filename }}</a></p>

        <div class="vulnerability">
            <h3>Security Vulnerability: File Execution</h3>
            <p>Since uploaded files are accessible via direct URL, any uploaded malicious file can be executed.</p>
            <p>Try uploading a file named "shell.php.jpg" with content:</p>
            <pre>&lt;?php system($_GET['cmd']); ?&gt;</pre>
            <p>Then access it with: <code>/uploads/[filename]?cmd=ls</code></p>
        </div>

        <a href="/upload" class="back-link">Upload Another File</a>
    </div>
</body>
</html>
"""

ADMIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Admin Panel</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }
        .container { max-width: 800px; margin: 50px auto; background: white; padding: 20px; border-radius: 5px; }
        h1 { color: #333; }
        .file-item { border-bottom: 1px solid #eee; padding: 10px 0; }
        .file-link { color: #4CAF50; text-decoration: none; }
        .back-link { color: #4CAF50; text-decoration: none; }
        .vulnerability { background-color: #fff0f0; border-left: 4px solid #ff6b6b; padding: 10px; margin: 15px 0; }
        .vulnerability h3 { color: #d32f2f; margin: 0 0 10px 0; }
        .vulnerability pre { background-color: #f1f1f1; padding: 10px; border-radius: 3px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Admin Panel</h1>

        <div class="vulnerability">
            <h3>Security Vulnerability: Path Traversal and File Access</h3>
            <p>This admin panel allows anyone to see all uploaded files without authentication.</p>
            <p>The files are executable and can be accessed directly via URL.</p>
            <p>Try uploading a malicious file and then accessing it directly.</p>
            <p>This is a critical security vulnerability!</p>
        </div>

        <h2>Uploaded Files</h2>

        {% if files %}
        <ul>
            {% for file in files %}
            <li class="file-item"><a href="/uploads/{{ file }}" class="file-link" target="_blank">{{ file }}</a></li>
            {% endfor %}
        </ul>
        {% else %}
        <p>No files uploaded yet.</p>
        {% endif %}

        <a href="/" class="back-link">← Back to Home</a>
    </div>
</body>
</html>
"""