import os
import json
import asyncio
from typing import Dict, Any, List
from datetime import datetime
from services.ai_service import analyze_attacks_with_ai
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from models import base
from database import get_db
from services.logging_service import LoggingService
from services.attack_engine import AttackEngine
import logging
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportGenerator:
    def __init__(self):
        self.logging_service = LoggingService()
        self.attack_engine = AttackEngine()

        # Set up Jinja2 templates
        template_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "templates", "reports"
        )
        self.env = Environment(loader=FileSystemLoader(template_dir))

        # Ensure template directory exists
        os.makedirs(template_dir, exist_ok=True)

    def generate_report(self, scan_id: int, report_format: str = "html", db: Session = None) -> Dict[str, Any]:
        """
        Generate a comprehensive security report for a scan
        """
        if db is None:
            db = next(get_db())

        try:
            # Get scan details
            scan = db.query(base.Scan).filter(base.Scan.id == scan_id).first()
            if not scan:
                raise Exception(f"Scan with ID {scan_id} not found")

            # Get lab details
            lab = scan.lab
            if not lab:
                raise Exception(f"Lab with ID {scan.lab_id} not found")

            # Get all logs for this scan
            logs = self.logging_service.get_logs_by_scan(scan_id, db)

            # Extract vulnerability findings
            vulnerability_logs = [
                log for log in logs if log.result == "vulnerability_detected"
            ]
            total_attempts = len(logs)
            vulnerabilities_detected = len(vulnerability_logs)

            # Group vulnerabilities by type
            vulnerability_types = {
                "sql_injection": [],
                "xss": [],
                "idor": [],
                "auth_bypass": [],
                "dir_traversal": [],
                "file_upload_abuse": [],
            }

            for log in vulnerability_logs:
                # Extract attack type from payload or metadata
                attack_type = self._extract_attack_type(log.payload)
                if attack_type in vulnerability_types:
                    vulnerability_types[attack_type].append(log)
                else:
                    # Use a general category for unknown types
                    category = "unknown"
                    if (
                        "sql" in log.payload.lower()
                        or "union" in log.payload.lower()
                        or "1=1" in log.payload.lower()
                    ):
                        category = "sql_injection"
                    elif (
                        "script" in log.payload.lower()
                        or "onerror" in log.payload.lower()
                        or "onload" in log.payload.lower()
                    ):
                        category = "xss"
                    elif (
                        "id" in log.payload.lower()
                        or "user_id" in log.payload.lower()
                        or "." in log.payload.lower()
                    ):
                        category = "idor"
                    elif "admin" in log.payload.lower() or "" in log.payload.lower():
                        category = "auth_bypass"
                    elif (
                        "../" in log.payload.lower()
                        or "etc/passwd" in log.payload.lower()
                    ):
                        category = "dir_traversal"
                    elif (
                        ".php" in log.payload.lower()
                        or ".jsp" in log.payload.lower()
                        or ".aspx" in log.payload.lower()
                    ):
                        category = "file_upload_abuse"
                    else:
                        category = "unknown"
                    vulnerability_types[category].append(log)

            # Process findings
            findings = []
            for attack_type, logs in vulnerability_types.items():
                if logs:
                    # Extract evidence from logs
                    evidence = []
                    for log in logs:
                        evidence_item = {
                            "payload": log.payload,
                            "request": log.request,
                            "response": log.response,
                        }
                        evidence.append(evidence_item)

                    # Generate recommendations based on attack type and evidence
                    recommendation = asyncio.run(
                        self._generate_recommendations(attack_type, evidence)
                    )

                    # Determine risk level
                    risk_level = self._determine_risk_level(attack_type)

                    # Generate detailed analysis
                    analysis = asyncio.run(
                        self._generate_analysis(attack_type, evidence)
                    )

                    findings.append(
                        {
                            "vulnerability_type": self._format_vulnerability_type(
                                attack_type
                            ),
                            "risk_level": risk_level,
                            "technical_explanation": analysis.get(
                                "technical_explanation", ""
                            ),
                            "example_exploitation": analysis.get(
                                "example_exploitation", ""
                            ),
                            "prevention": analysis.get("prevention", ""),
                            "secure_code_recommendation": recommendation.get(
                                "secure_code_recommendation", ""
                            ),
                            "evidence": evidence,
                        }
                    )

            # Calculate overall risk level
            overall_risk = self._calculate_overall_risk(findings)

            # Generate AI recommendations
            ai_recommendations = self._generate_ai_recommendations(
                scan.attack_type, findings
            )
            ongoing_recommendations = self._generate_ongoing_recommendations()

            # Prepare report data
            report_data = {
                "lab_name": lab.name,
                "generated_at": datetime.now().strftime("%B %d, %Y at %H:%M:%S"),
                "year": datetime.now().year,
                "total_attempts": total_attempts,
                "vulnerabilities_detected": vulnerabilities_detected,
                "overall_risk": overall_risk,
                "findings": findings,
                "logs": [
                    {
                        "timestamp": log.timestamp.strftime("%B %d, %Y at %H:%M:%S")
                        if log.timestamp
                        else "",
                        "payload": log.payload,
                        "result": log.result,
                        "severity": log.severity,
                    }
                    for log in logs
                ],
                "ai_recommendations": ai_recommendations,
                "ongoing_recommendations": ongoing_recommendations,
            }

            # Generate report content based on format
            report_content = self._generate_report_content(report_data, report_format)

            # Create report record in database
            report_data_db = {
                "scan_id": scan_id,
                "user_id": scan.user_id,
                "content": json.dumps(report_data),  # Store raw data for future use
                "format": report_format,
                "status": "generated",
            }

            report = base.Report(
                scan_id=report_data_db["scan_id"],
                user_id=report_data_db["user_id"],
                content=report_data_db["content"],
                format=report_data_db["format"],
                status=report_data_db["status"]
            )
            db.add(report)
            db.commit()
            db.refresh(report)

            return {
                "report_id": report.id,
                "scan_id": scan_id,
                "format": report_format,
                "content": report_content,
                "generated_at": datetime.now().strftime("%B %d, %Y at %H:%M:%S"),
                "status": "generated",
            }

        except Exception as e:
            logger.error(f"Error generating report for scan {scan_id}: {str(e)}")
            raise

    def _generate_report_content(self, report_data: Dict[str, Any], report_format: str) -> str:
        try:
            template_name = f"{report_format}.html"
            template = self.env.get_template(template_name)

            # Add custom filter for EOL to BR conversion
            @template.environment.filter
            def eol2br(value):
                if not value:
                    return ""
                return value.replace("\n", "<br>")

            # Render the template
            html_content = template.render(report=report_data)

            if report_format == "html":
                return html_content
            elif report_format == "markdown":
                # Convert HTML to Markdown
                # This is a simplified conversion - for production use, consider using a proper HTML-to-Markdown converter
                return self._html_to_markdown(html_content)
            elif report_format == "pdf":
                # Generate PDF from HTML
                # Convert HTML to PDF using WeasyPrint
                html = HTML(string=html_content)
                pdf_content = html.write_pdf()
                return pdf_content

        except Exception as e:
            logger.error(
                f"Error generating report content for format {report_format}: {str(e)}"
            )
            # Return fallback content
            return f"Error generating {report_format} report: {str(e)}"

    def _extract_attack_type(self, payload: str) -> str:
        """
        Extract attack type from payload based on common patterns
        """
        if not payload:
            return "unknown"

        payload_lower = payload.lower()

        # SQL Injection patterns
        if any(
            pattern in payload_lower
            for pattern in ["'", "' or 1=1", "' or 'a'='a", "union select"]
        ):
            return "sql_injection"

        # XSS patterns
        elif any(
            pattern in payload_lower
            for pattern in ["<script>", "onerror=", "onload=", "javascript:"]
        ):
            return "xss"

        # IDOR patterns
        elif any(
            pattern in payload_lower
            for pattern in ["id=", "user_id=", "user=", "admin=", "1", "2", "100"]
        ):
            return "idor"

        # Authentication bypass patterns
        elif any(
            pattern in payload_lower for pattern in ["admin'--", "' or 1=1#", "root'--"]
        ):
            return "auth_bypass"

        # Directory traversal patterns
        elif any(
            pattern in payload_lower
            for pattern in ["../../../../", "..%2f", "../", "/etc/passwd"]
        ):
            return "dir_traversal"

        # File upload patterns
        elif any(
            pattern in payload_lower
            for pattern in [".php", ".jsp", ".aspx", ".shell.", '".jpg']
        ):
            return "file_upload_abuse"

        return "unknown"

    def _format_vulnerability_type(self, attack_type: str) -> str:
        """
        Format attack type to a user-friendly name
        """
        type_map = {
            "sql_injection": "SQL Injection",
            "xss": "Cross-Site Scripting (XSS)",
            "idor": "Insecure Direct Object Reference (IDOR)",
            "auth_bypass": "Authentication Bypass",
            "dir_traversal": "Directory Traversal",
            "file_upload_abuse": "File Upload Abuse",
            "unknown": "Unknown Vulnerability",
        }
        return type_map.get(attack_type, attack_type.replace("_", " ").title())

    def _determine_risk_level(self, attack_type: str) -> str:
        """
        Determine risk level based on attack type
        """
        risk_map = {
            "sql_injection": "critical",
            "auth_bypass": "critical",
            "dir_traversal": "critical",
            "file_upload_abuse": "critical",
            "idor": "high",
            "xss": "medium",
            "unknown": "low",
        }
        return risk_map.get(attack_type, "low")

    def _calculate_overall_risk(self, findings: List[Dict]) -> str:
        """
        Calculate overall risk level based on findings
        """
        if not findings:
            return "low"

        # Count critical and high risk findings
        critical_count = sum(1 for f in findings if f["risk_level"] == "critical")
        high_count = sum(1 for f in findings if f["risk_level"] == "high")
        medium_count = sum(1 for f in findings if f["risk_level"] == "medium")
        low_count = sum(1 for f in findings if f["risk_level"] == "low")

        # Determine overall risk
        if critical_count > 0:
            return "critical"
        elif high_count > 0:
            return "high"
        elif medium_count > 0:
            return "medium"
        elif low_count > 0:
            return "low"
        else:
            return "low"

    async def _generate_analysis(
        self, attack_type: str, evidence: List[Dict]
    ) -> Dict[str, str]:
        """
        Generate technical analysis based on attack type and evidence using AI
        """
        # Create a mock attack log from evidence
        attack_log = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "payload": evidence[0]["payload"] if evidence else "",
            "request": evidence[0]["request"] if evidence else "",
            "response": evidence[0]["response"] if evidence else "",
            "result": "vulnerability_detected",
            "severity": "critical"
            if attack_type
            in ["sql_injection", "auth_bypass", "dir_traversal", "file_upload_abuse"]
            else "high"
            if attack_type == "idor"
            else "medium"
            if attack_type == "xss"
            else "low",
        }

        # Use AI service to analyze (this will handle all the analysis in one go)
        # We need to provide the scan details context for the AI
        scan_details = {
            "lab_name": "N/A",
            "attack_type": self._format_vulnerability_type(attack_type),
        }

        result = await analyze_attacks_with_ai([attack_log], scan_details)

        if result.success and result.analysis:
            analysis = result.analysis
            return {
                "technical_explanation": analysis.get("technical_explanation", ""),
                "example_exploitation": analysis.get("example_exploitation", ""),
                "prevention": analysis.get("prevention", ""),
            }
        else:
            # Fallback to original analysis if AI fails
            return self._generate_analysis_fallback(attack_type)

    def _generate_analysis_fallback(self, attack_type: str) -> Dict[str, str]:
        """
        Fallback analysis implementation for when AI service is unavailable
        """
        analysis = {
            "technical_explanation": "",
            "example_exploitation": "",
            "prevention": "",
        }

        if attack_type == "sql_injection":
            analysis["technical_explanation"] = (
                "SQL Injection occurs when an attacker is able to insert or 'inject' a SQL query via the input data from the client to the application. "
                "A successful SQL injection exploit can read sensitive data from the database, modify database data (Insert/Update/Delete), "
                "execute administration operations on the database (such as shutdown the DBMS), recover the content of a given file "
                "present on the DBMS file system, and in some cases issue commands to the operating system."
            )
            analysis["example_exploitation"] = (
                "An attacker can exploit this vulnerability by entering malicious SQL code in input fields. For example, "
                "instead of entering a valid username such as 'admin', they might enter 'admin' OR '1'='1'. This makes "
                "the SQL query always return true, bypassing authentication and potentially allowing access to all user data."
            )
            analysis["prevention"] = (
                "To prevent SQL injection, always use parameterized queries or prepared statements instead of string concatenation. "
                "Validate and sanitize all inputs on the server side. Use web application firewalls (WAFs) to detect and block common SQL injection patterns."
            )

        elif attack_type == "xss":
            analysis["technical_explanation"] = (
                "Cross-Site Scripting (XSS) occurs when an attacker is able to inject client-side scripts into web pages viewed by other users. "
                "This happens when an application includes untrusted data in a web page without proper validation or escaping. "
                "XSS attacks enable attackers to circumvent access controls such as the same-origin policy."
            )
            analysis["example_exploitation"] = (
                "An attacker can exploit this vulnerability by injecting a JavaScript payload, such as '<script>alert('XSS')</script>', "
                "into input fields. When another user views the page containing this payload, their browser executes the script, "
                "potentially stealing session cookies, redirecting to malicious sites, or defacing the web page."
            )
            analysis["prevention"] = (
                "To prevent XSS, validate and sanitize all user inputs on the server side, encode all user inputs before outputting them to HTML, "
                "use Content Security Policy (CSP), and set appropriate HTTP headers like 'X-XSS-Protection'."
            )

        elif attack_type == "idor":
            analysis["technical_explanation"] = (
                "Insecure Direct Object Reference (IDOR) occurs when an application exposes a reference to an internal implementation "
                "object, such as a file, directory, or database key, and fails to properly validate user privileges to access that object. "
                "This allows an attacker to bypass authorization and access resources they shouldn't be able to."
            )
            analysis["example_exploitation"] = (
                "An attacker can exploit this vulnerability by modifying request parameters to access other users' resources. "
                "For example, changing the user ID in a URL from 'user_id=1' to 'user_id=2' to access another user's account information."
            )
            analysis["prevention"] = (
                "To prevent IDOR, implement proper access control checks on every request. Instead of using direct object references, "
                "use indirect object references (mappings). Validate user authorization for each resource access request."
            )

        elif attack_type == "auth_bypass":
            analysis["technical_explanation"] = (
                "Authentication Bypass occurs when an attacker can gain access to an application without providing valid credentials. "
                "This can happen due to vulnerabilities in the authentication mechanism that allow brute force attacks, "
                "SQL injection, or other techniques to circumvent login requirements."
            )
            analysis["example_exploitation"] = (
                "An attacker can exploit this vulnerability by entering malicious input in login forms, such as 'admin' OR '1'='1' "
                "for the username and any password. If the application doesn't properly validate inputs, this can bypass "
                "authentication and grant access to the administrative panel."
            )
            analysis["prevention"] = (
                "To prevent authentication bypass, use strong password policies, implement multi-factor authentication, "
                "use parameterized queries for database authentication checks, implement account lockout after multiple failed attempts, "
                "and use secure authentication libraries."
            )

        elif attack_type == "dir_traversal":
            analysis["technical_explanation"] = (
                "Directory Traversal (or Path Traversal) is an attack that allows an attacker to read files outside the web root "
                "directory, potentially gaining access to sensitive system files, configuration files, or credentials. "
                "This occurs when user-supplied input is used to construct file system paths without proper validation."
            )
            analysis["example_exploitation"] = (
                "An attacker can exploit this vulnerability by requesting files like '../etc/passwd' in URL parameters. "
                "If the application doesn't sanitize these inputs, it will read and display the contents of the system's password file, "
                "revealing sensitive user information."
            )
            analysis["prevention"] = (
                "To prevent directory traversal, validate and sanitize all user inputs used in file paths. Use a whitelist of allowed file names, "
                "use a base directory and combine with user input rather than using user input directly, and disable file system access "
                "when not necessary."
            )

        elif attack_type == "file_upload_abuse":
            analysis["technical_explanation"] = (
                "File Upload Abuse occurs when an application allows users to upload files without proper validation of file type, "
                "content, or name. This can allow attackers to upload malicious files such as web shells, scripts, or executable files "
                "that can be executed on the server, leading to complete system compromise."
            )
            analysis["example_exploitation"] = (
                "An attacker can exploit this vulnerability by uploading a file with a double extension like 'shell.php.jpg', "
                "where the file content is actually a malicious PHP script. If the application only checks the file extension "
                "and not the content, it might allow the upload. The attacker can then navigate to the uploaded file and execute it."
            )
            analysis["prevention"] = (
                "To prevent file upload abuse, validate uploaded files by checking the file extension, MIME type, and file content. "
                "Store uploaded files outside the web root directory and use random filenames. Implement antivirus scanning on uploads, "
                "and use secure file permissions."
            )

        else:
            analysis["technical_explanation"] = (
                "This is an unknown vulnerability type. The system detected suspicious activity but couldn't classify it. "
                "Further investigation may be required to determine the exact nature of this issue."
            )
            analysis[
                "example_exploitation"
            ] = "The detection system identified potentially malicious behavior but couldn't identify a specific exploitation pattern."
            analysis["prevention"] = (
                "Implement comprehensive input validation and sanitization for all user input. Use a web application firewall. "
                "Perform regular security audits and penetration testing."
            )

        return analysis

    async def _generate_recommendations(
        self, attack_type: str, evidence: List[Dict]
    ) -> Dict[str, str]:
        """
        Generate secure code recommendations using AI analysis
        """
        # Create a mock attack log from evidence
        attack_log = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "payload": evidence[0]["payload"] if evidence else "",
            "request": evidence[0]["request"] if evidence else "",
            "response": evidence[0]["response"] if evidence else "",
            "result": "vulnerability_detected",
            "severity": "critical"
            if attack_type
            in ["sql_injection", "auth_bypass", "dir_traversal", "file_upload_abuse"]
            else "high"
            if attack_type == "idor"
            else "medium"
            if attack_type == "xss"
            else "low",
        }

        # Use AI service to analyze (this will handle all the analysis in one go)
        # We need to provide the scan details context for the AI
        scan_details = {
            "lab_name": "N/A",
            "attack_type": self._format_vulnerability_type(attack_type),
        }

        result = await analyze_attacks_with_ai([attack_log], scan_details)

        if result.success and result.analysis:
            # Extract secure code recommendation from AI analysis
            return {
                "secure_code_recommendation": result.analysis.get(
                    "secure_code_recommendation", ""
                )
            }
        else:
            # Fallback to original recommendations if AI fails
            return self._generate_recommendations_fallback(attack_type)

    def _generate_recommendations_fallback(self, attack_type: str) -> Dict[str, str]:
        """
        Fallback recommendations implementation for when AI service is unavailable
        """
        recommendations = {"secure_code_recommendation": ""}

        if attack_type == "sql_injection":
            recommendations[
                "secure_code_recommendation"
            ] = """  # DON'T (Vulnerable)
query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"

# DO (Secure)
import sqlite3
import hashlib

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Use parameterized queries
username = "admin"
password = "mypassword"
hash_password = hashlib.sha256(password.encode()).hexdigest()
cursor.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?", (username, hash_password))
user = cursor.fetchone()

conn.close()
"""

        elif attack_type == "xss":
            recommendations[
                "secure_code_recommendation"
            ] = """  # DON'T (Vulnerable)
response.write("<div>" + userInput + "</div>")

# DO (Secure)
import html

# HTML encode user input
escaped_input = html.escape(userInput)
response.write("<div>" + escaped_input + "</div>")

# In JavaScript (frontend), sanitize before insertion
def sanitizeInput(input) {
    const div = document.createElement('div');
    div.textContent = input;
    return div.innerHTML;
}
"""

        elif attack_type == "idor":
            recommendations[
                "secure_code_recommendation"
            ] = """  # DON'T (Vulnerable)
@app.route('/user/<int:user_id>')
def get_user(user_id):
    # Directly use user_id from URL parameter
    user = db.query(User).filter(User.id == user_id).first()
    return user

# DO (Secure)
@app.route('/user/profile')
def get_user_profile():
    # Get user ID from authenticated session
    current_user_id = get_current_user_id() # From authentication system

    # Only allow access to own profile
    user = db.query(User).filter(User.id == current_user_id).first()
    return user

# Alternative: Use indirect references
@app.route('/user/profile/<string:profile_id>')
def get_user_profile(profile_id):
    # Map profile_id to actual user ID with access check
    user_id = profile_id_map.get(profile_id)
    if user_id is None:
        raise HTTPException(status_code=404)

    # Verify user has permission to access this profile
    current_user_id = get_current_user_id()
    if not has_permission(current_user_id, user_id):
        raise HTTPException(status_code=403)

    user = db.query(User).filter(User.id == user_id).first()
    return user
"""

        elif attack_type == "auth_bypass":
            recommendations[
                "secure_code_recommendation"
            ] = """  # DON'T (Vulnerable)
@app.route('/login')
def login():
    username = request.form['username']
    password = request.form['password']

    # Vulnerable query
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    result = db.execute(query).fetchone()

    if result:
        session['logged_in'] = True
        return redirect('/dashboard')

# DO (Secure)
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/login')
def login():
    username = request.form['username']
    password = request.form['password']

    # Use parameterized query and password hashing
    user = db.query(User).filter(User.username == username).first()

    if user and check_password_hash(user.password_hash, password):
        session['logged_in'] = True
        return redirect('/dashboard')

    return render_template('login.html', error='Invalid credentials')

# Also implement:
# - Multi-factor authentication
# - Account lockout after multiple failed attempts
# - Rate limiting on login endpoint
"""

        elif attack_type == "dir_traversal":
            recommendations[
                "secure_code_recommendation"
            ] = """  # DON'T (Vulnerable)
@app.route('/download', methods=['GET'])
def download_file():
    filename = request.args.get('file', 'default.txt')
    file_path = os.path.join('uploads', filename)
    return send_file(file_path)

# DO (Secure)
import os
from pathlib import Path

@app.route('/download', methods=['GET'])
def download_file():
    filename = request.args.get('file', '')

    # Define the base directory
    base_dir = Path('uploads')

    # Create a safe path
    file_path = base_dir / filename

    # Ensure the file is within the intended directory
    try:
        file_path = file_path.resolve()
        if not file_path.is_relative_to(base_dir.resolve()):
            raise FileNotFoundError("Access denied")
    except Exception:
        raise FileNotFoundError("File not found")

    # Check if file exists
    if not file_path.exists():
        raise FileNotFoundError("File not found")

    return send_file(file_path)

# Alternative approach: Use a whitelist of allowed files
ALLOWED_FILES = ['document1.pdf', 'image.jpg', 'data.csv']

@app.route('/download', methods=['GET'])
def download_file():
    filename = request.args.get('file', '')
    if filename not in ALLOWED_FILES:
        raise FileNotFoundError("File not found")

    file_path = os.path.join('uploads', filename)
    return send_file(file_path)
"""

        elif attack_type == "file_upload_abuse":
            recommendations[
                "secure_code_recommendation"
            ] = """  # DON'T (Vulnerable)
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    filename = file.filename
    file.save(os.path.join('uploads', filename))
    return redirect(f'/uploads/{filename}')

# DO (Secure)
import os
import uuid
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
UPLOAD_FOLDER = 'uploads'

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    # Get file extension
    ext = file.filename.rsplit('.', 1)[1].lower()

    # Check if extension is allowed
    if ext not in ALLOWED_EXTENSIONS:
        return 'Invalid file extension', 400

    # Generate secure filename
    filename = str(uuid.uuid4()) + '.' + ext

    # Save file
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    # Return URL to file (but make sure web server doesn't execute it)
    return redirect(f'/uploads/{filename}')

# In Apache/Nginx configuration, disable execution in uploads directory
# Apache:
# <Directory "/var/www/uploads">
# php_flag engine off
# Options -Indexes -ExecCGI
# </Directory>

# Also implement:
# - Content-type validation
# - File size limits
# - Antivirus scanning
# - Store files outside web root
# - Use separate domain for uploaded files
"""

        else:
            recommendations[
                "secure_code_recommendation"
            ] = """  # Implement comprehensive input validation and sanitization
# Use security libraries for common vulnerabilities
# Implement a web application firewall (WAF)
# Perform regular security audits and penetration testing
# Keep all dependencies up to date
# Implement logging and monitoring for suspicious activity
# Follow the principle of least privilege in your application and server configuration
"""

        return recommendations

    def _generate_ai_recommendations(
        self, attack_type: str, findings: List[Dict]
    ) -> str:
        """
        Generate AI-derived recommendations for the overall assessment
        """
        if not findings:
            return "No vulnerabilities detected. Your application appears to be secure."

        # Count critical vulnerabilities
        critical_count = sum(1 for f in findings if f["risk_level"] == "critical")
        high_count = sum(1 for f in findings if f["risk_level"] == "high")
        medium_count = sum(1 for f in findings if f["risk_level"] == "medium")

        recommendations = []

        if critical_count > 0:
            recommendations.append(
                "Critical vulnerabilities detected. These require immediate attention as they could lead to complete system compromise."
            )

        if high_count > 0:
            recommendations.append(
                f"{high_count} high-risk vulnerabilities detected. These should be addressed within the next sprint."
            )

        if medium_count > 0:
            recommendations.append(
                f"{medium_count} medium-risk vulnerabilities detected. These should be addressed in your next security review."
            )

        if critical_count == 0 and high_count == 0 and medium_count == 0:
            recommendations.append(
                "No critical, high, or medium vulnerabilities detected. Your application has good security posture."
            )

        # Add general recommendations
        recommendations.append(
            "Consider implementing automated security testing in your CI/CD pipeline."
        )
        recommendations.append(
            "Regularly update your third-party dependencies to patch known vulnerabilities."
        )
        recommendations.append(
            "Provide security training for your development team on common OWASP Top 10 vulnerabilities."
        )
        recommendations.append(
            "Perform periodic penetration testing on your applications."
        )
        recommendations.append(
            "Implement a vulnerability management program to track and remediate security issues."
        )

        return "\n\n".join(recommendations)

    def _generate_ongoing_recommendations(self) -> List[str]:
        """
        Generate ongoing recommendations for security improvements
        """
        return [
            "Implement automated security testing in CI/CD pipeline",
            "Establish a vulnerability disclosure policy",
            "Schedule regular penetration testing",
            "Implement comprehensive logging and monitoring",
            "Establish a security training program for developers",
            "Perform monthly security reviews",
            "Implement secure coding standards",
            "Integrate security into your development lifecycle (DevSecOps)",
            "Consider adopting a Web Application Firewall (WAF)",
            "Regularly review and update your security policies",
        ]

    def _html_to_markdown(self, html_content: str) -> str:
        """
        Convert HTML to Markdown (simplified conversion)
        """
        import re

        if not isinstance(html_content, str):
            return ""
        markdown_content = html_content
        markdown_content = markdown_content.replace("<h1>", "# ").replace(
            "</h1>", "\n\n"
        )
        markdown_content = markdown_content.replace("<h2>", "## ").replace(
            "</h2>", "\n\n"
        )
        markdown_content = markdown_content.replace("<h3>", "### ").replace(
            "</h3>", "\n\n"
        )
        markdown_content = markdown_content.replace("<strong>", "**").replace(
            "</strong>", "**"
        )
        markdown_content = markdown_content.replace("<em>", "_").replace("</em>", "_")
        markdown_content = re.sub(r"<br\s*/?>", "\n", markdown_content, flags=re.I)
        markdown_content = re.sub(r"\n\s*\n+", "\n\n", markdown_content)
        return markdown_content
