
import time
from datetime import datetime
import requests

from models.check_result import CheckResult
from models.endpoint import Endpoint

session = requests.Session()

class HttpChecker:
    def check(self, endpoint: Endpoint) -> CheckResult:
        start = time.time()

        try:
            response = session.head(endpoint.url, timeout=5, allow_redirects=True)
            latency_ms = int((time.time() - start) * 1000)

            return CheckResult(
                id=None,
                endpoint_id=endpoint.id,
                ts=datetime.now().isoformat(),
                latency_ms=latency_ms,
                status="OK" if response.ok else "ERROR",
                http_status=response.status_code,
                error_type=None if response.ok else "HTTP_ERROR",
                error_message=None if response.ok else f"HTTP {response.status_code}",
            )

        except requests.exceptions.Timeout:
            return CheckResult(
                id=None,
                endpoint_id=endpoint.id,
                ts=datetime.now().isoformat(),
                latency_ms=None,
                status="ERROR",
                http_status=None,
                error_type="TIMEOUT",
                error_message="Request timed out",
            )

        except requests.exceptions.RequestException as e:
            return CheckResult(
                id=None,
                endpoint_id=endpoint.id,
                ts=datetime.now().isoformat(),
                latency_ms=None,
                status="ERROR",
                http_status=None,
                error_type="REQUEST_ERROR",
                error_message=str(e),
            )
