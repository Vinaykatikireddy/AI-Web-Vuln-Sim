from flask import Flask, request, jsonify, render_template, redirect, url_for
import os
import uuid

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Helper function to check allowed file extensions
# This is vulnerable because it only checks the filename, not the actual file content
# Malicious files with double extensions (e.g., file.php.jpg) can bypass this check

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route for homepage
@app.route('/')
def home():
    return render_template('index.html')

# Route for file upload form
@app.route('/upload')
def upload_form():
    return render_template('upload.html')

# Route for handling file upload
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file and allowed_file(file.filename):
        # Vulnerability: No server-side validation of file content
        # The check only validates the extension, not the actual file content

        # Vulnerability: Using secure_filename but still vulnerable to path traversal
        # The filename is sanitized but not properly validated

        # Generate random filename to prevent conflicts
        filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()

        # Vulnerability: No check for malicious file content
        # A user could upload a malicious PHP, JSP, or executable file
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Vulnerability: Files are accessible directly via URL
        # This allows remote code execution if a web shell is uploaded
        return render_template('upload_success.html', filename=filename)
    else:
        return render_template('upload.html', error='File type not allowed')

# Route for viewing uploaded files (vulnerable)
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # Vulnerability: Direct access to uploaded files without authentication
    # This allows anyone to access any uploaded file

    # Vulnerability: No validation that the file is safe to serve
    # This allows execution of uploaded malicious files
    return app.send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Admin endpoint to view uploaded files (vulnerable)
@app.route('/admin')
def admin():
    # Vulnerability: No authentication check
    # Any user can access the admin panel

    files = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
            files.append(filename)

    return render_template('admin.html', files=files)

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
    with open('templates/index.html', 'w') as f:
        f.write(index_template)

if not os.path.exists('templates/upload.html'):
    upload_template = """
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
    with open('templates/upload.html', 'w') as f:
        f.write(upload_template)

if not os.path.exists('templates/upload_success.html'):
    success_template = """
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
    with open('templates/upload_success.html', 'w') as f:
        f.write(success_template)

if not os.path.exists('templates/admin.html'):
    admin_template = """
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
    with open('templates/admin.html', 'w') as f:
        f.write(admin_template)

# Health check endpoint
@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    # Run application
    app.run(host='0.0.0.0', port=5000, debug=False)