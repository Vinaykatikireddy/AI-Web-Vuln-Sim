from flask import Flask, request, jsonify, render_template_string, redirect, url_for
import os
import uuid
import templates

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

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
    return render_template_string(templates.HOME_PAGE)

# Route for file upload form
@app.route('/upload')
def upload_form():
    return render_template_string(templates.UPLOAD_PAGE)

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
        return render_template_string(templates.SUCCESS_PAGE, filename=filename)
    else:
        return render_template_string(templates.UPLOAD_PAGE, error='File type not allowed')

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

    return render_template_string(templates.ADMIN_PAGE, files=files)

# Health check endpoint
@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    # Run application
    app.run(host='0.0.0.0', port=5000, debug=False)