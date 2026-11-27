import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse, parse_qs

import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from models import base

logger = logging.getLogger(__name__)


class ReconService:
    """Bounded, same-origin reconnaissance and scoped HTTP execution for registered labs."""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "AI-Web-Vuln-Sim-Analyst/1.0",
                "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
            }
        )

    @staticmethod
    def is_same_origin(base_url: str, target_url: str) -> bool:
        """Ensure outbound requests stay strictly within the registered lab's origin."""
        base_parsed = urlparse(base_url)
        target_parsed = urlparse(target_url)
        return (
            target_parsed.scheme in {"http", "https"}
            and target_parsed.scheme == base_parsed.scheme
            and target_parsed.netloc == base_parsed.netloc
        )

    def map_surface(self, base_url: str, max_pages: int = 8) -> Dict[str, Any]:
        """Crawl same-origin pages of a lab and extract forms, inputs, and query parameters."""
        visited: set[str] = set()
        queue: List[str] = [base_url]
        pages: List[Dict[str, Any]] = []
        forms: List[Dict[str, Any]] = []

        while queue and len(visited) < max_pages:
            current_url = queue.pop(0)
            if current_url in visited or not self.is_same_origin(base_url, current_url):
                continue
            visited.add(current_url)

            try:
                resp = self.session.get(current_url, timeout=self.timeout, allow_redirects=True)
            except Exception as exc:
                pages.append({"url": current_url, "error": str(exc)})
                continue

            parsed = urlparse(resp.url)
            query_params = list(parse_qs(parsed.query).keys())
            content_type = resp.headers.get("Content-Type", "")
            page_info: Dict[str, Any] = {
                "url": resp.url,
                "path": parsed.path or "/",
                "status_code": resp.status_code,
                "content_length": len(resp.content),
                "query_params": query_params,
            }

            if "html" in content_type.lower():
                soup = BeautifulSoup(resp.text, "html.parser")
                title = soup.title.string.strip() if soup.title and soup.title.string else None
                page_info["title"] = title

                for form in soup.find_all("form"):
                    action = urljoin(resp.url, form.get("action") or "")
                    if not self.is_same_origin(base_url, action):
                        continue
                    method = (form.get("method") or "GET").upper()
                    inputs = []
                    for inp in form.find_all(["input", "textarea", "select"]):
                        name = inp.get("name")
                        if name:
                            inputs.append(
                                {
                                    "name": name,
                                    "type": inp.get("type", inp.name),
                                }
                            )
                    forms.append(
                        {
                            "page": parsed.path or "/",
                            "action": urlparse(action).path or "/",
                            "method": method,
                            "inputs": inputs,
                        }
                    )

                for anchor in soup.find_all("a", href=True):
                    next_url = urljoin(resp.url, anchor["href"]).split("#")[0]
                    if self.is_same_origin(base_url, next_url) and next_url not in visited:
                        queue.append(next_url)

            pages.append(page_info)

        return {
            "base_url": base_url,
            "pages_discovered": pages,
            "forms_discovered": forms,
        }

    def send_scoped_request(
        self,
        db: Session,
        scan_id: int,
        base_url: str,
        method: str = "GET",
        path: str = "/",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        payload_label: str = "",
    ) -> Dict[str, Any]:
        """Execute a single HTTP request scoped to the lab's origin and persist a Log row."""
        target_url = urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
        if not self.is_same_origin(base_url, target_url):
            raise ValueError(f"Blocked out-of-scope URL: {target_url}")

        method_upper = method.upper()
        if method_upper not in {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}:
            raise ValueError(f"Unsupported HTTP method: {method}")

        try:
            resp = self.session.request(
                method=method_upper,
                url=target_url,
                params=params,
                data=data,
                headers=headers,
                timeout=self.timeout,
                allow_redirects=False,
            )
            body_excerpt = resp.text[:800] if resp.text else ""
            req_summary = f"{method_upper} {resp.url}"
            if data:
                req_summary += f" | body={data}"
            resp_summary = (
                f"Status: {resp.status_code}, Length: {len(resp.content)}, "
                f"Location: {resp.headers.get('Location', 'none')}\n{body_excerpt}"
            )

            log_row = base.Log(
                scan_id=scan_id,
                request=req_summary,
                response=resp_summary,
                payload=payload_label or str(data or params or ""),
                result="observed",
                severity=None,
            )
            db.add(log_row)
            db.commit()
            db.refresh(log_row)

            return {
                "log_id": log_row.id,
                "url": resp.url,
                "status_code": resp.status_code,
                "content_length": len(resp.content),
                "location": resp.headers.get("Location"),
                "body_excerpt": body_excerpt,
            }
        except Exception as exc:
            log_row = base.Log(
                scan_id=scan_id,
                request=f"{method_upper} {target_url}",
                response=f"Error: {exc}",
                payload=payload_label or str(data or params or ""),
                result="error",
                severity=None,
            )
            db.add(log_row)
            db.commit()
            db.refresh(log_row)
            return {
                "log_id": log_row.id,
                "url": target_url,
                "error": str(exc),
            }
